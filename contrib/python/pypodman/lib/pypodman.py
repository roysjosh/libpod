#!/usr/bin/env python3
"""Remote podman client."""

import logging
import os
import sys

import lib.actions
from lib import PodmanArgumentParser

assert lib.actions  # silence pyflakes


def main():
    """Entry point."""
    # Setup logging so we use stderr and can change logging level later
    # Do it now before there is any chance of a default setup hardcoding crap.
    log = logging.getLogger()
    fmt = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s',
                            '%Y-%m-%d %H:%M:%S %Z')
    stderr = logging.StreamHandler(stream=sys.stderr)
    stderr.setFormatter(fmt)
    log.addHandler(stderr)
    log.setLevel(logging.WARNING)

    parser = PodmanArgumentParser()
    args = parser.parse_args()

    log.setLevel(args.log_level)
    logging.debug('Logging initialized at level {}'.format(
        logging.getLevelName(logging.getLogger().getEffectiveLevel())))

    def want_tb():
        """Add traceback when logging events."""
        return log.getEffectiveLevel() == logging.DEBUG

    try:
        if not os.path.exists(args.run_dir):
            os.makedirs(args.run_dir)
    except PermissionError as e:
        logging.critical(e, exc_info=want_tb())
        sys.exit(6)

    # class_(args).method() are set by the sub-command's parser
    returncode = None
    try:
        obj = args.class_(args)
    except Exception as e:
        logging.critical(repr(e), exc_info=want_tb())
        logging.warning('See subparser "{}" configuration.'.format(
            args.subparser_name))
        sys.exit(5)

    try:
        returncode = getattr(obj, args.method)()
    except AttributeError as e:
        logging.critical(e, exc_info=want_tb())
        logging.warning('See subparser "{}" configuration.'.format(
            args.subparser_name))
        returncode = 3
    except KeyboardInterrupt:
        pass
    except (
            ConnectionRefusedError,
            ConnectionResetError,
            TimeoutError,
    ) as e:
        logging.critical(e, exc_info=want_tb())
        logging.info('Review connection arguments for correctness.')
        returncode = 4

    return 0 if returncode is None else returncode


if __name__ == '__main__':
    sys.exit(main())
