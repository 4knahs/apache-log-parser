import utils
from logger import warn, info, debug, error
import datetime
from event_types import EVENT_LOG, EVENT_TIMER
from table_logger import TableLogger
import os

class Plugin:

    TIMERS = [10, 120]

    def __init__(self):
        self.paths = {}
        self.codes = {}
        self.users = {}
        self.hosts = {}

    def __call__(self, event, parameter):

        if event == EVENT_LOG:
            clf = parameter['clf']
            request = parameter['request']

            self.aggregate(clf, request)

        elif event == EVENT_TIMER:
            if parameter == 10:
                self.stats_event()
            else:
                self.threshold_event()            
        
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

    def threshold_event(self):
        pass

    def stats_event(self):
        collections = [self.paths, self.codes, self.users, self.hosts]
        titles = ['Paths', 'Codes', 'Users', 'Hosts']

        # The following is a bad if we are allowing multiple plugins ;) Just for demo purposes 
        _=os.system("clear")

        for i,c in enumerate(collections):
            self.print_stat(titles[i], c) # Show stats
            c.clear() # Clear stats

    def increment(self, collection, key):
        collection[key] = collection.get(key, 0) + 1

    def print_stat(self, title, collection):
        if len(collection) > 0:
            tbl = TableLogger(columns='{},count'.format(title))
            for p in sorted(collection, key=collection.get, reverse=True)[:5]:
                tbl(p, collection[p])
            
    