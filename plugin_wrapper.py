from timer_thread import TimerThread
from threading import Event
from logger import warn, info, debug, error
from event_types import EVENT_LOG, EVENT_TIMER

class PluginWrapper:
    def __init__(self, clas):
        self.plugin = clas
        # We can register multiple timers
        self.timer_events = []

    def stop_timers():
        for t in self.timer_events:
            t.set() # Sets the timer stop event

    def schedule_timer(self, plug, time):
        stop_event = Event()
        TimerThread(stop_event, time, plug).start()
        self.timer_events.append(stop_event)

    def __call__(self, conn, args):

        plug = self.plugin(args)
        ts = self.plugin.__dict__.get('TIMERS',[])
        for t in ts:
            self.schedule_timer(plug, t)

        debug("Wrapper alive")
        while True:
            try:
                r = conn.recv()
                plug(EVENT_LOG, r)
            except EOFError as err:
                error('recv failed')
            except (KeyboardInterrupt, SystemExit):
                debug('recv interrupted')
        debug("Wrapper done!")
