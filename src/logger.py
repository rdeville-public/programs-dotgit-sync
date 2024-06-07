#!/usr/bin/env python3

import argparse
import logging
import re


def init_logger(args: argparse.Namespace, log: logging.Logger) -> None:
    str_fmt = "%(asctime)-15s %(levelname)-8s %(name)-10s %(message)s"
    json_fmt = """\
{
    "time":"%(asctime)s",
    "level":"%(levelname)s",
    "name":"%(name)s",
    "message": "%(message)s"
}\
"""

    if args.verbose == 0:
        log.setLevel(logging.WARNING)
    elif args.verbose == 1:
        log.setLevel(logging.INFO)
    elif args.verbose >= 2:
        log.setLevel(logging.DEBUG)
    else:
        raise LookupError(f"Verbosity of {args.verbose} is not valid.")

    if re.match("json|Json|JSON*", args.log_format):
        stream_formatter = logging.Formatter(json_fmt)
    elif re.match("string|String|STRING*", args.log_format):
        stream_formatter = logging.Formatter(str_fmt)
    else:
        raise LookupError("Log format should be either `json` or `string`.")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    log.addHandler(stream_handler)
