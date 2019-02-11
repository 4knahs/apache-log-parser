import os
from contextlib import contextmanager
from dateutil.parser import parse
from logger import warn, info, debug, error, set_verbose, logger_to_stdout, set_silent
import re
from collections import defaultdict, namedtuple

# PEP 343 for file error handling https://www.python.org/dev/peps/pep-0343/
@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()

def to_datetime(str):
    d = parse(str[:11] + " " + str[12:])
    debug('{} converted to {}'.format(str, d))
    return d

def top_path(path):
    path_format = re.compile(
        r"^(?P<path>/[^/]*)"
    )

    Path = namedtuple('Path', ['path'])

    match = path_format.match(path)

    if match:
        return Path(**match.groupdict()).path

    return None
