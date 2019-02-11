import unittest
from parser import parse_line, CLF, CLFRequest
import plugins.stats as pstats
from event_types import EVENT_LOG, EVENT_TIMER

class TestParser(unittest.TestCase):

    def test_alerts(self):

        # We will just repeat the same line multiple times to simulate a high request/rate
        line = parse_line('172.16.0.3 - - [25/Sep/2002:14:04:19 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"')

        stats = pstats.Plugin()

        for _ in range(10*120):
            stats(EVENT_LOG, line)

        # As requested the alert prints the requests, here we pass silent=True to omit those lines
        self.assertEqual(stats.alert(silent=True), True)

        # Event 5 minutes after the previous ones should clear the alert
        line = parse_line('172.16.0.3 - - [25/Sep/2002:14:09:19 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"')

        # Process event
        stats(EVENT_LOG, line)

        self.assertEqual(stats.alert(silent=True), False)

        # 119 events exactly one minute and 59 seconds after last event
        line = parse_line('172.16.0.3 - - [25/Sep/2002:14:11:18 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"')

        for _ in range(10*120 - 1):
            stats(EVENT_LOG, line)

        self.assertEqual(stats.alert(silent=True), True)

    def test_top_pages(self):
        # TODO: hire me to implement this method :P
        pass

    def test_line_parser(self):

        lines = [
            '172.16.0.3 - - [25/Sep/2002:14:04:19 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"',
            '64.242.88.10 - - [07/Mar/2004:16:05:49 -0800] "GET /twiki/bin?topicparent=Main.ConfigurationVariables HTTP/1.1" 401 12846',
            '93.114.45.13 - - [17/May/2015:10:05:04 +0000] "GET /reset.css HTTP/1.1" 200 1015 "http://www.semicomplete.com/articles/dynamic-dns-with-dhcp/" "Mozilla/5.0 (X11; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0"',
            '1.1.1.2 - - [11/Nov/2016:03:04:55 +0100] "GET /" 200 83 "-" "-" - 9221 1.1.1.1',
            '127.0.0.1 - - [11/Nov/2016:14:24:21 +0100] "GET /uno dos" 404 298 "-" "-" - 400233 1.1.1.1',
            '127.0.0.1 - - [11/Nov/2016:14:23:37 +0100] "GET /uno dos HTTP/1.0" 404 298 "-" "-" - 385111 1.1.1.1',
            '1.1.1.1 - - [11/Nov/2016:00:00:11 +0100] "GET /icc HTTP/1.1" 302 - "-" "XXX XXX XXX" - 6160 11.1.1.1',
            '1.1.1.1 - - [11/Nov/2016:00:00:11 +0100] "GET /icc/ HTTP/1.1" 302 - "-" "XXX XXX XXX" - 2981 1.1.1.1'
        ]

        matches = [
            {
                'clf': CLF(
                    remote_host='172.16.0.3', 
                    rfc931='-', 
                    auth_user='-', 
                    date='25/Sep/2002:14:04:19 +0200', 
                    request='GET / HTTP/1.1', 
                    status='401', 
                    bytes='-'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/', 
                    version='HTTP/1.1')
            },
            {
                'clf': CLF(
                    remote_host='64.242.88.10', 
                    rfc931='-', 
                    auth_user='-', 
                    date='07/Mar/2004:16:05:49 -0800', 
                    request='GET /twiki/bin?topicparent=Main.ConfigurationVariables HTTP/1.1', 
                    status='401', 
                    bytes='12846'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/twiki/bin?topicparent=Main.ConfigurationVariables', 
                    version='HTTP/1.1')
            },
            {
                'clf': CLF(
                    remote_host='93.114.45.13', 
                    rfc931='-', 
                    auth_user='-', 
                    date='17/May/2015:10:05:04 +0000', 
                    request='GET /reset.css HTTP/1.1', 
                    status='200', 
                    bytes='1015'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/reset.css', 
                    version='HTTP/1.1')
            },
            {
                'clf': CLF(
                    remote_host='1.1.1.2', 
                    rfc931='-', 
                    auth_user='-', 
                    date='11/Nov/2016:03:04:55 +0100', 
                    request='GET /', 
                    status='200', 
                    bytes='83'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/', 
                    version=None)
            },
            {
                'clf': CLF(
                    remote_host='127.0.0.1', 
                    rfc931='-', 
                    auth_user='-', 
                    date='11/Nov/2016:14:24:21 +0100', 
                    request='GET /uno dos', 
                    status='404', 
                    bytes='298'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/uno dos', 
                    version=None)
            },
            {
                'clf': CLF(
                    remote_host='127.0.0.1', 
                    rfc931='-', 
                    auth_user='-', 
                    date='11/Nov/2016:14:23:37 +0100', 
                    request='GET /uno dos HTTP/1.0', 
                    status='404', 
                    bytes='298'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/uno dos', 
                    version='HTTP/1.0')
            },
            {
                'clf': CLF(
                    remote_host='1.1.1.1', 
                    rfc931='-', 
                    auth_user='-', 
                    date='11/Nov/2016:00:00:11 +0100', 
                    request='GET /icc HTTP/1.1', 
                    status='302', 
                    bytes='-'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/icc', 
                    version='HTTP/1.1')
            },
            {
                'clf': CLF(
                    remote_host='1.1.1.1', 
                    rfc931='-', 
                    auth_user='-', 
                    date='11/Nov/2016:00:00:11 +0100', 
                    request='GET /icc/ HTTP/1.1', 
                    status='302', 
                    bytes='-'), 
                'request': CLFRequest(
                    method='GET', 
                    path='/icc/', 
                    version='HTTP/1.1')
            }
        ]

        for i,line in enumerate(lines):
            p = parse_line(line)

            self.assertEqual(p['clf'], matches[i]['clf'])
            self.assertEqual(p['request'], matches[i]['request'])
    
 

       
if __name__ == '__main__':
    unittest.main()