# Common Log Format Parser

## Requirements

This app was tested with Python 3.5.2.

To install the requirements:

```bash
$ pip install -r requirements.txt
```

## How to run

To run the parser against a log file do as follows:

```bash
python main.py -l <log-file>
```

For help:

```bash
$ python main.py -h
usage: main.py [-h] [-f] [-l FILE] [-v] [-s]

Reads logs in the Apache Combined Log Format and the Common Log Format.

optional arguments:
  -h, --help  show this help message and exit
  -f          Tail the log file.
  -l FILE     Path to logfile.
  -v          Enable verbose.
  -s          Silent. Superseedes -v and disables logging.
```

## Plugins

Plugins are added by creating a new python file in the plugins folder.
This python file needs to implement a Plugin class as follows:

```python
class Plugin:

    # Add the time periods at which you want to receive an EVENT_TIMER
    TIMERS = [] 

    def __init__(self):
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
```

Check the `plugins/sample_plugin.py` for an example.

## Plugin Events

The event types are defined in `event_types.py`. 

### EVENT_LOG Event

When the event is a log, the parameters consist of a dictionary with the `clf` and `request` keys.
The clf (`parameters['clf']`) is a named tuple, thus one can access the fields like `clf.remote_host`.
The available fields are:

* `remote_host`
* `rfc931`
* `auth_user`
* `date`
* `request`
* `status`
* `bytes`

The request (`parameters['request']`) consists of the parsed request field from clf.
Similarly the available fields are:

* `method`
* `path`
* `version`

There is a `sample_plugin.py` file that you can use to create your first plugin.
For more details on the format of the fields check the [W3 Logging documentation](https://www.w3.org/Daemon/User/Config/Logging.html) or check the tests in `test_parse.py`.

### EVENT_TIMER Event

Occurs at the times specified by the `TIMERS` list declared in the respective plugin class (if present).
Its parameter is the frequency of the timer.
Check `plugins/stats.py` for an example on how to use the timers.

## Generating logs

To generate apache logs in `/tmp` do the following:

```bash
cd access_log_generator
docker build -t faker .
docker run -v /tmp:/usr/src/logs faker
tail -f /tmp/*.log # might want to tail the specific file
```

Note that these logs are in the Combined Log Format.
Nonetheless we only deal with the Common Log Format, which ignores the last two fields:

* The referer HTTP request header. This gives the site that the client reports having been referred from.
* The User-Agent HTTP request header. This is the identifying information that the client browser reports about itself.

For more information regarding the format check the [httpd apache log documentation](https://httpd.apache.org/docs/2.4/logs.html).

## Design decisions

* The basic log parsing is done only once and assures correct order of events.
* Processing of parsed logs is done by plugins.
* Plugins abstract processes and receive the parsed logs via pipes / message passing.
* Each process has its own timer threads to schedule events.

What could improve:

* Log rotation - many apps with logs use logrotate, in such case it would be worth to had inotify capabilities to check when the file gets moved.
* Single threaded scheduling of events - atm there is a ThreadTimer per timed event, this could/should easily be a single thread with a queue of waiting times.
* Monitoring of pipes - should assure that event production/consumption is not lagging behind. 

