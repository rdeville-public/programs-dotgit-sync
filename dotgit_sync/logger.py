#!/usr/bin/env python3
"""Logger facility."""

import argparse
import logging
import re


_WARNING = 0
_INFO = 1
_DEBUG = 2


def init_logger(args: argparse.Namespace, log: logging.Logger) -> None:
    """Initiliaze logger and format.

    Args:
        args: Arguments passed to programs
        log: Python logger
    """
    str_fmt = "%(asctime)-8s %(levelname)-8s %(name)-10s %(message)s"
    json_fmt = """\
{
    "time":"%(asctime)s",
    "level":"%(levelname)s",
    "name":"%(name)s",
    "message": "%(message)s"
}\
"""

    if args.verbose == _WARNING:
        log.setLevel(logging.WARNING)
    elif args.verbose == _INFO:
        log.setLevel(logging.INFO)
    elif args.verbose >= _WARNING:
        log.setLevel(logging.DEBUG)
    else:
        error_msg = f"Verbosity of {args.verbose} is not valid."
        raise LookupError(error_msg)

    if re.match(r"json|Json|JSON*", args.log_format):
        stream_formatter = logging.Formatter(json_fmt)
    elif re.match(r"string|String|STRING*", args.log_format):
        stream_formatter = logging.Formatter(str_fmt)
    else:
        error_msg = "Log format should be either `json` or `string`."
        raise LookupError(error_msg)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    log.addHandler(stream_handler)
