from queue import LifoQueue
from threading import Thread
import cherrypy
import traceback

class Pool:
    def __init__(self, cls_list):
        self.cls_list = cls_list
        self._make_queues()

    def _make_queues(self):
        self.queues = dict()

        self.threads = []
        for cls_ in self.cls_list:
            instance = cls_()
            q = LifoQueue()
            th = Thread(target=self.loop, args=(instance, q,))

            self.queues[cls_] = q
            self.threads.append(th)

    def start(self):
        for th in self.threads:
            th.start()

    def stop(self):
        for q in self.queues.values():
            q.put(None)
        for th in self.threads:
            th.join()

        self._make_queues()

    def put(self, cls_, item):
        target = self.queues[cls_]
        target.put(item)

    def loop(self, instance, queue):
        item = queue.get()
        while item is not None:
            self.handle_item(instance, item)
            item = queue.get()

    def handle_item(self, item):
        raise NotImplementedError('Please implement this')


class Crawler(Pool):
    def handle_item(self, instance, v):
        print(instance.name)
        try:
            results = getattr(instance, v.verb)(*v.args)
            for r in results:
                if hasattr(r, 'source') and not r.source:
                    r.source = instance.name
            v.output.put(results)
        except ValueError as e:
            cherrypy.engine.log('Crawler exception %s' % repr(e))
            cherrypy.engine.log(traceback.format_exc())
