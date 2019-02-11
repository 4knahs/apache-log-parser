# To handle file rotation
import inotify.adapters
import os
from utils import opened_w_error
import re
import time

from logger import warn, info, debug, error, set_verbose, logger_to_stdout, set_silent
from collections import defaultdict, namedtuple

# ?P - to make the group name accessible via name
clf_format = re.compile( 
    r"^(?P<remote_host>[\d\.]+)\s" 
    r"(?P<rfc931>\S+)\s"        # TODO: double check if optional 
    r"(?P<auth_user>\S+)\s"     # TODO: double check if optional
    r"\[(?P<date>.+)\]\s"
    r'\"(?P<request>.*?)\"\s'
    r"(?P<status>\d+)\s"
    r"(?P<bytes>\S*)"
    #r'\s"(?P<referer>.*?)"\s?'     # This is optional
    #r'"(?P<user_agent>.*?)"\s*' # This is optional
)

request_format = re.compile(
    r"^(?P<method>.*?)"        # This can be messed up with telnet so optional
    r"\s(?P<path>.*?)"
    r"\s?(?P<version>HTTP/.*)?$" 
)

CLF = namedtuple('CLF',
    ['remote_host', 'rfc931', 'auth_user', 'date', 'request',
    'status', 'bytes']) #, 'referer', 'user_agent'] )

CLFRequest = namedtuple('CLFRequest',
    ['method', 'path', 'version'])

def parse_clf(line):
    match = clf_format.match(line)

    if match:
        return CLF(**match.groupdict())
    else:
        error('Failed processing: {}'.format(line))
        
def parse_clf_request(request):
    request_match = request_format.match(request)

    if request_match:
        return CLFRequest(**request_match.groupdict())
    else:
        # The request processing can fail since it comes from the client.
        # Can easily come broken from fuzzers, malformed requests, etc.
        # "The request line exactly as it came from the client."
        # https://www.w3.org/Daemon/User/Config/Logging.html
        error('Failed processing request: {}'.format(request))

def parse_line(line):

    clf = parse_clf(line)
    req = None

    if clf:
        req = parse_clf_request(clf.request)

    return {'clf': clf, 'request': req}

def tail(file, manager, tail=False):
    #notifier = inotify.adapters.Inotify()

    while True:
        try:
            # File might not be present on rotation or to be created
            if not os.path.exists(file):
                warn('File {} does not exist.'.format(file))
                time.sleep(1)
                continue

            #notifier.add_watch(logfile)
            
            with opened_w_error(file, "r") as (f, err):
                if err:
                    error("IOError: + {}".format(err))
                else:
                    if tail:
                        f.seek(0,2)
                        tail = False

                    for line in f.readlines():
                        # Sends the message to all registered plugs
                        manager.send_to_plugs(parse_line(line))

        #except inotify.calls.InotifyError:
        #    sleep(1)

        # Avoid errors on interrupt
        except (KeyboardInterrupt, SystemExit):
            manager.stop_plugins()
            break
