import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.process.plugins import SimplePlugin
from queue import Queue, Empty
from collections import namedtuple
from concurrent import Crawler
import parsing
import json

from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

PoolItem = namedtuple('PoolItem', ['verb', 'args'])

class Search:
    def __init__(self):
        self.engines_suggest = []
        self.engines_search = []
        self.q_suggest = Queue()
        self.q_search = Queue()
        self.add_engines(parsing.sites)
        self.pool_suggest = Crawler(cls_list=self.engines_suggest, output=self.q_suggest)
        self.pool_search = Crawler(cls_list=self.engines_search, output=self.q_search)

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
        for engine in self.engines_suggest:
            self.pool_suggest.put(engine, PoolItem('suggest', (keyword,)))

        failure = 0
        while failure < 5:
            results = set()
            try:
                results.update(self.q_suggest.get(timeout=1))
            except Empty:
                failure += 1
            yield list(results)

    def search(self, keyword, from_id):
        for engine in self.engines_search:
            self.pool_search.put(engine, PoolItem('search', (keyword, from_id + 1, None)))

        failure = 0
        while failure < 5:
            results = set()
            try:
                results.update(self.q_suggest.get(timeout=1))
            except Empty:
                failure += 1
            yield list(results)

class WSHandler(WebSocket):
    def opened(self):
        print('Opened')

    def received_message(self, msg):
        print(str(msg))
        # cherrypy.engine.publish('websocket-broadcast', msg)
        # self.send(msg, binary=False)
        try:
            j = json.loads(msg)
            verb, params = j['verb'], j['params']
            if verb == 'suggest':
                self.ws_suggest(params['keyword'])
            elif verb == 'search':
                self.ws_serach(params['keyword'], params['from_id'])
            else:
                raise ValueError('Unknown verb. (suggest, serach)')
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            cherrypy.engine.log('Exception - %s' % repr(e))

    def closed(self, code, reason='A client left'):
        # cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))
        cherrypy.engine.log(reason)

    def ws_suggest(self, keyword):
        results = Queue()
        cherrypy.engine.publish('detour_suggest', keyword, results)
        item = results.get()
        while item is not None:
            msg = json.dumps({'keyword': keyword, 'results': item})
            cherrypy.engine.publish('websocket-broadcast', msg)
            item = results.get()

    def ws_search(self, keyword, from_id):
        results = Queue()
        cherrypy.engine.publish('detour_search', keyword, from_id, results)
        r = results.get()
        while r is not None:
            d = r.items()
            d['keyword'], d['from_id'] = keyword, from_id
            cherrypy.engine.publish('websocket-broadcast', msg)
            item = results.get()


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

        for results in generator:
            print('Got results!' + repr(results))
            bucket.put(results)
        bucket.put(None)

    def search_handler(self, keyword, from_id, bucket):
        self.bus.log('Search ' + repr(keyword) + ' from ID ' + repr(from_id))
        generator = self.search_daemon.search(keyword, from_id)

        for results in generator:
            bucket.put(results)
        bucket.put(None)


TIMEOUT = 8

class Detour:
    def __init__(self, public):
        self.public = public

    @cherrypy.expose
    def index(self):
        return serve_file(self.public + '/index.html')

    @cherrypy.expose
    def suggest(self, keyword):
        results = Queue()
        cherrypy.engine.publish('detour_suggest', keyword, results)
        return str(results.get(block=True, timeout=TIMEOUT))

    @cherrypy.expose
    def search(self, keyword, from_id=0):
        results = Queue()
        cherrypy.engine.publish('detour_search', keyword, from_id, results)
        return str(results.get(block=True, timeout=TIMEOUT))

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler
        cherrypy.log("Handler created: %s" % repr(handler))
