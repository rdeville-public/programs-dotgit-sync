#!/usr/bin/env python3
"""Check filetypes of template files."""

import inspect
import logging
import pathlib

import magic

from . import const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def get_filetype(filepath: pathlib.Path) -> str:
    """Return the filetype of from file provided as filepath.

    Args:
        filepath: Path to the file

    Returns:
        String with the filetype
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    ft = magic.from_file(filepath, mime=True).split("/")[-1]
    if ft != "plain" and not ft.startswith("x-"):
        return ft
    ext = "." + filepath.name.split(".")[-1]
    for ft, exts in const.FILETYPES.items():
        if ext in exts:
            return ft
    return "plain"
