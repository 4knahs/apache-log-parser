import utils
from logger import warn, info, debug, error
import datetime
from event_types import EVENT_LOG, EVENT_TIMER
from table_logger import TableLogger
import os
from collections import deque
import math

class Plugin:

    WINDOW = 120
    TIMERS = [10]

    def __init__(self, args=[]):

        if len(args) > 0:
            self.threshold = int(args[0])
        else:
            self.threshold = 10

        self.paths = {}
        self.codes = {}
        self.users = {}
        self.hosts = {}
        self.on_alert = False

        # Will use 1s buckets of log events on a "circular buffer"
        self.time_buckets = [[] for i in range(self.WINDOW)]
        self.current_index = 0
        self.last_event = None

    def __call__(self, event, parameter):

        if event == EVENT_LOG:
            clf = parameter['clf']
            request = parameter['request']

            # Keeps overall statistics
            self.aggregate(clf, request)

            # Keeps the circular buffer of events per second
            self.add_to_time_buckets(parameter)

        elif event == EVENT_TIMER:
            
            # Generates the 10s statistics
            self.stats_event()  

            # Generates alerts
            self.alert()
        
        else:
            warn('Unexpected event {}'.format(event))


    def aggregate(self, clf, request):

        if request.path and utils.top_path(request.path):
            self.increment(self.paths, utils.top_path(request.path))
        
        if clf.status:
            self.increment(self.codes, clf.status)
            
        if clf.auth_user and clf.auth_user != '-':
            self.increment(self.users, clf.auth_user)

        if clf.remote_host and clf.remote_host != '-':
            self.increment(self.hosts, clf.remote_host)

    def add_to_time_buckets(self, parameter):
        clf = parameter['clf']
        request = parameter['request']
        
        if self.last_event == None:

            # Just store the first event
            self.time_buckets[self.current_index].append(parameter)

        else:
            current_date = utils.to_datetime(clf.date)

            last_date = utils.to_datetime(self.last_event['clf'].date)

            diff = math.floor((current_date - last_date).total_seconds())

            for i in range(1, diff + 1): # ignored if diff == 0
                new_index = (self.current_index + i) % self.WINDOW
                # Fill the intermediate indexes with no log events
                self.time_buckets[new_index] = []

            # Max len of the circular buffer is WINDOW
            self.current_index = (self.current_index + diff) % self.WINDOW

            # Given the previous loop this should already be an array
            self.time_buckets[self.current_index].append(parameter)

        self.last_event = parameter

    def total_requests(self):

        total = 0

        for bucket in self.time_buckets:
            total += len(bucket) # Len should be O(1) in python

        return total

    def list_requests(self):
        lst = []

        for bucket in self.time_buckets:
            lst = lst + bucket
        
        return lst

    def alert(self, silent=False):

        total = self.total_requests()
        avg = total / self.WINDOW

        self.print_stat('Watchlist', {
            'Avg. frequency': avg,
            'Total requests': total,
            'Threshold': self.threshold,
            }, value_title='value')

        if avg >= self.threshold:
            self.print_stat('ALERT', 
                {'High traffic': 'hits = {}, triggered at {}'.format(avg, datetime.datetime.now())}, 
                value_title='Status')
            if not silent:
                for r in self.list_requests():
                    print(r)

            self.on_alert = True
            return True

        # Alert is over
        if self.on_alert:
            self.alert_recover()

        self.on_alert = False
        return False

    def alert_recover(self):
        self.print_stat('ALERT', {'High traffic': 'Recovered!'}, value_title='Status')

    def stats_event(self):
        collections = [self.paths, self.codes, self.users, self.hosts]
        titles = ['Paths', 'Codes', 'Users', 'Hosts']

        # The following is a bad if we are allowing multiple plugins ;) Just for demo purposes 
        #_=os.system("clear")
        print("")

        for i,c in enumerate(collections):
            self.print_stat(titles[i], c) # Show stats
            c.clear() # Clear stats

    def increment(self, collection, key):
        collection[key] = collection.get(key, 0) + 1

    def print_stat(self, title, collection, value_title='count'):
        if len(collection) > 0:
            tbl = TableLogger(columns='{},{}'.format(title, value_title))
            for p in sorted(collection, key=collection.get, reverse=True)[:5]:
                tbl(p, collection[p])
            
    