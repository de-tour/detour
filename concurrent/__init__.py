from queue import PriorityQueue
from threading import Thread
from collections import namedtuple

class Pool:
    def __init__(self, capacity=15, output = None):
        self.capacity = capacity
        self.output = output
        self._make_queues()

    def _make_queues(self):
        self.queues = []
        self.threads = []
        for _ in range(self.capacity):
            q = PriorityQueue()
            th = Thread(target=self.loop, args=(q,))
            self.queues.append(q)
            self.threads.append(th)

    def start(self):
        for th in self.threads:
            th.start()

    def stop(self):
        for q in self.queues:
            q.put((0, None))
        for th in self.threads:
            th.join()

        self._make_queues()

    def put(self, item, priority=1):
        smallest = None
        target = None
        for q in self.queues:
            size = q.qsize()
            if smallest is None:
                smallest = size
                target = q
            elif smallest > size:
                smallest = size
                target = q
        target.put((priority, item))

    def loop(self, queue):
        priority, item = queue.get()
        while item is not None:
            self.handle_item(item)
            queue.task_done()
            item = queue.get()

    def handle_item(self, item):
        raise NotImplementedError('Please implement this')


class Crawler(Pool):
    def handle_item(self, func):
        try:
            results = func()
            self.output.put(results)
        except ValueError as e:
            pass
