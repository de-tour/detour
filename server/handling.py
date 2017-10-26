import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.process.plugins import SimplePlugin
from queue import Queue, Empty
from collections import namedtuple
from concurrent import Crawler
import parsing
import json
import traceback
from urllib.parse import unquote

from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

PoolItem = namedtuple('PoolItem', ['verb', 'args', 'output'])

class Search:
    def __init__(self):
        self.engines_suggest = []
        self.engines_search = []
        self.add_engines(parsing.sites)
        self.pool_suggest = Crawler(cls_list=self.engines_suggest)
        self.pool_search = Crawler(cls_list=self.engines_search)

    def start(self):
        self.pool_suggest.start()
        self.pool_search.start()

    def add_engines(self, engines):
        for Engine in engines:
            if parsing.is_balancer(Engine):
                self.add_engines(Engine.balance())
            else:
                if parsing.can_suggest(Engine):
                    self.engines_suggest.append(Engine)
                if parsing.can_search(Engine):
                    self.engines_search.append(Engine)

    def stop(self):
        self.pool_suggest.stop()
        self.pool_search.stop()

    def suggest(self, keyword):
        if not keyword:
            yield []
            return

        output = Queue()
        for engine in self.engines_suggest:
            self.pool_suggest.put(engine, PoolItem('suggest', (keyword,), output))

        failure = 0
        result_set = set()
        while failure < 1:
            try:
                result_set.update(output.get(timeout=1))
            except Empty:
                failure += 1

            ordered_results = parsing.rank_list(result_set, keyword)[0:10]
            result_set = set(ordered_results)
            yield ordered_results

    def search(self, keyword, from_id):
        if not keyword:
            yield []
            return

        output = Queue()
        for engine in self.engines_search:
            if not parsing.is_meta(engine):
                self.pool_search.put(engine, PoolItem('search', (keyword, from_id + 1, None), output))
            else:
                for site in parsing.domains:
                    filtered = engine.site_filter(site, keyword)
                    self.pool_search.put(engine, PoolItem('search', (filtered, from_id + 1, None), output))

        failure = 0
        result_set = set()
        while failure < 5:
            try:
                new_results = set(output.get(timeout=1))
                print('Search: %d unique results' % len(result_set))
                yield parsing.rank_list(new_results - result_set, keyword)
                result_set.update(new_results)
            except Empty:
                failure += 1

class WSHandler(WebSocket):
    def opened(self):
        cherrypy.engine.log('WebSocket opened')

    def received_message(self, msg):
        cherrypy.engine.log('Received ' + str(msg))
        try:
            params = json.loads(str(msg))
            verb = params['verb']
            if verb == 'suggest':
                self.ws_suggest(unquote(params['keyword']))
            elif verb == 'search':
                self.ws_search(unquote(params['keyword']), params['from_id'])
            else:
                raise ValueError('Unknown verb. (suggest, serach)')
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            cherrypy.engine.log('Handler Exception - %s' % repr(e))
            cherrypy.engine.log(traceback.format_exc())

    def closed(self, code, reason):
        cherrypy.engine.log('A client left')

    def ws_suggest(self, keyword):
        results = Queue()
        cherrypy.engine.publish('detour_suggest', keyword, results)
        generator = results.get()

        for item in generator:
            if item:
                msg = json.dumps({'from': keyword, 'results': item})
                cherrypy.engine.publish('websocket-broadcast', msg)

    def ws_search(self, keyword, from_id):
        results = Queue()
        cherrypy.engine.publish('detour_search', keyword, from_id, results)
        generator = results.get()

        for r_list in generator:
            if r_list:
                d = {
                    'results': [r.items() for r in r_list],
                    'keyword': keyword,
                    'from_id': from_id,
                }
                cherrypy.engine.publish('websocket-broadcast', json.dumps(d))


class Daemon(SimplePlugin):
    def __init__(self, bus):
        SimplePlugin.__init__(self, bus)

    def start(self):
        self.bus.log('Daemon plugin starts')
        self.priority = 70

        self.search_daemon = Search()
        self.search_daemon.start()
        self.bus.subscribe('detour_suggest', self.suggest_handler)
        self.bus.subscribe('detour_search', self.search_handler)

    def stop(self):
        self.bus.unsubscribe('detour_suggest', self.suggest_handler)
        self.bus.unsubscribe('detour_search', self.search_handler)
        self.search_daemon.stop()

        self.bus.log('Daemon plugin stops')

    def suggest_handler(self, keyword, bucket):
        self.bus.log('Suggest ' + repr(keyword))
        generator = self.search_daemon.suggest(keyword)
        print("suggest_handler: got generator")
        bucket.put(generator)

    def search_handler(self, keyword, from_id, bucket):
        self.bus.log('Search ' + repr(keyword) + ' from ID ' + repr(from_id))
        generator = self.search_daemon.search(keyword, from_id)
        print("search_handler: got generator")
        bucket.put(generator)




class Detour:
    def __init__(self, public):
        self.public = public

    @cherrypy.expose
    def index(self, q=None):
        return serve_file(self.public + '/index.html')

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler
        cherrypy.log("Handler created: %s" % repr(handler))
