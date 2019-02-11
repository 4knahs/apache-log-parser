import argparse
import parser
from logger import warn, info, debug, error, set_verbose, logger_to_stdout, set_silent
from plugin_manager import PluginManager

def main():
    # Handle command line inputs
    p = argparse.ArgumentParser(description="Reads logs in the Apache Combined Log Format and the Common Log Format.")
    p.add_argument('-f', help='Tail the log file.', dest='tail', action='store_true')
    p.add_argument('-l', help='Path to logfile.', dest='file')
    p.add_argument('-v', help='Enable verbose.', dest='verbose', action='store_true')
    p.add_argument('-s', help='Silent. Superseedes -v and disables logging.', dest='silent', action='store_true')
    p.set_defaults(verbose=False, silent=False, file='/tmp/access.log', tail=False)

    args = p.parse_args()

    logger_to_stdout()

    if args.verbose:
        set_verbose()

    if args.silent:
        set_silent()

    manager = PluginManager()
    manager.load_plugins()

    parser.tail(args.file, manager, tail=args.tail)

if __name__ == '__main__':
    main()