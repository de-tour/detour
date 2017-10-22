from queue import PriorityQueue
from threading import Thread


class Pool:
    def __init__(self, cls_list, output):
        self.output = output
        self.cls_list = cls_list
        self._make_queues()

    def _make_queues(self):
        # self.instance_dict = {}
        self.queues = dict()

        self.threads = []
        for cls_ in self.cls_list:
            instance = cls_()
            q = PriorityQueue()
            th = Thread(target=self.loop, args=(instance, q,))

            # self.instance_dict[cls_] = instance
            self.queues[cls_] = q
            self.threads.append(th)

    def start(self):
        for th in self.threads:
            th.start()

    def stop(self):
        for q in self.queues.values():
            q.put((0, None))
        for th in self.threads:
            th.join()

        self._make_queues()

    def put(self, cls_, item, priority=1):
        target = self.queues[cls_]
        target.put((priority, item))

    def loop(self, instance, queue):
        priority, item = queue.get()
        while item is not None:
            self.handle_item(instance, item)
            priority, item = queue.get()

    def handle_item(self, item):
        raise NotImplementedError('Please implement this')


class Crawler(Pool):
    def handle_item(self, instance, v):
        try:
            results = getattr(instance, v.verb)(*v.args)
            for r in results:
                if not r.source:
                    r.source = instance.name
            self.output.put(results)
        except ValueError as e:
            pass
