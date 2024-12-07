#!/usr/bin/env python3
"""Set of utility to manipulate data."""

import inspect
import logging
import pathlib

from . import const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def merge_json_dict(src: dict | None, update: dict) -> dict:
    """Deeply merge json dictionary.

    Args:
        src: Initial dictionary
        update: New dictionary that will be merge into the initial dictionary

    Return:
        The merged dictionary
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    if src is None:
        return update

    for key, value in update.items():
        if key not in src:
            src[key] = value
            continue
        if isinstance(value, dict):
            merge_json_dict(src[key], value)
        elif isinstance(value, list):
            merge_json_list(src[key], value)
        else:  # isinstance(value, (str, int, float)):
            src[key] = value
    return src


def merge_json_list(src: list, update: list) -> list:
    """Deeply merge json list or concat if item does not exists.

    Args:
        src: Initial list
        update: New list that will be concat into the initial dictionary

    Return:
        The merged list
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if src and not isinstance(src[0], type(update[0])):
        error_msg = f"Different types! {type(src[0])}, {type(update[0])}"
        raise ValueError(error_msg)

    if not src or len(src) == 0:
        src = update
    else:
        for item in update:
            if item not in src:
                src.append(item)
    return src
