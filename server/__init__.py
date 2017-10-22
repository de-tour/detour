import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.process.plugins import SimplePlugin
from queue import Queue, Empty

from concurrent import Crawler
import parsing

class Search:
    def __init__(self):
        self.engines_suggest = []
        self.engines_search = []
        self.q_suggest = Queue()
        self.q_search = Queue()
        self.pool_suggest = Crawler(output=self.q_suggest)
        self.pool_search = Crawler(output=self.q_search)
        self.add_engines(parsing.sites)

    def start(self):
        self.pool_suggest.start()
        self.pool_search.start()

    def add_engines(self, engines):
        for Engine in engines:
            if parsing.is_balancer(Engine):
                self.add_engines(Engine.balance())
            else:
                if parsing.can_suggest(Engine):
                    self.engines_suggest.append(Engine())
                if parsing.can_search(Engine):
                    self.engines_search.append(Engine())

    def stop(self):
        self.pool_suggest.stop()
        self.pool_search.stop()

    def suggest(self, keyword):
        results = set()
        for engine in self.engines_suggest:
            print(engine.name)
            raw_results = engine.suggest(keyword)
            for r in raw_results:
                r = r.strip()
                if r:
                    results.add(r)
            # self.pool_suggest.put(lambda: engine.suggest(keyword))
        # results = self.q_suggest.get()
        return list(results)

    def search(self, keyword, from_id):
        return []


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
        results = self.search_daemon.suggest(keyword)
        bucket.put(results)

    def search_handler(self, keyword, from_id, bucket):
        self.bus.log('Search ' + repr(keyword) + ' from ID ' + repr(from_id))
        results = self.search_daemon.search(keyword, from_id)
        bucket.put(results)


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
