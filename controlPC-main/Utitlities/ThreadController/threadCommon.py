import threading
import queue

class ThreadCommonQueue:
    def __init__(self):
        self.thread_queue = queue.Queue()
    def get_event(self):
        return self.thread_queue.get();
    def set_event(self,event):
        self.thread_queue.put(event)
