import utils
from event_types import EVENT_LOG, EVENT_TIMER

class Plugin:

    # Add the time periods at which you want to receive an EVENT_TIMER
    TIMERS = [] 

    def __init__(self, args=[]):
        pass

    def __call__(self, event, parameters):

        if event == EVENT_LOG:
            # New log
            pass
        elif event == EVENT_TIMER:
            # Timer based event
            pass
        else:
            # Unexpected event
            warn('Unexpected event {}'.format(event))