#!/usr/bin/env python3
"""Logger facility."""

import argparse
import re

import coloredlogs


_WARNING_LVL = 0
_INFO_LVL = 1
_DEBUG_LVL = 2
_WARNING = "WARNING"
_INFO = "INFO"
_DEBUG = "DEBUG"

_STR_FMT = "%(asctime)-8s %(levelname)-8s %(name)-10s %(message)s"
_JSON_FMT = """\
{
    "level":"%(levelname)s",
    "time":"%(asctime)s",
    "name":"%(name)s",
    "message": "%(message)s"
}\
"""


def init_logger(args: argparse.Namespace) -> None:
    """Initiliaze logger and format.

    Args:
        args: Arguments passed to programs
        log: Python logger
    """
    if re.match(r"json|Json|JSON*", args.log_format):
        coloredlogs.install(fmt=_JSON_FMT)
    elif re.match(r"string|String|STRING*", args.log_format):
        coloredlogs.install(fmt=_STR_FMT)
    else:
        error_msg = "Log format should be either `json` or `string`."
        raise LookupError(error_msg)

    if args.verbose == _WARNING_LVL:
        coloredlogs.set_level(_WARNING)
    elif args.verbose == _INFO_LVL:
        coloredlogs.set_level(_INFO)
    elif args.verbose >= _DEBUG_LVL:
        coloredlogs.set_level(_DEBUG)
    else:
        error_msg = f"Verbosity of {args.verbose} is not valid."
        raise LookupError(error_msg)
