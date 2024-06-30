from Utitlities.ThreadController.threadCommon import ThreadCommonQueue
import queue
# import mouse
from pynput import mouse
def mouse_thread_func(mouseQueue):
    print("Mouse Thread begin")
    while True:
        event = mouseQueue.get_event()
        eventType, arg = event
        if eventType == "QUIT":
            break
        if eventType == "MOVE":
            x,y = arg
            mouse.move(x,y, absolute=True)
        elif eventType == "CLICK":
            mouse.click(arg)
