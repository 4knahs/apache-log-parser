from threading import Thread, Event
from event_types import EVENT_LOG, EVENT_TIMER

class TimerThread(Thread):
    def __init__(self, event, time, plug):
        Thread.__init__(self)
        self.stopped = event
        self.plug = plug
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            self.plug(EVENT_TIMER, self.time)