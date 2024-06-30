#!/usr/bin/env python3
"""Check filetypes of template files."""

import inspect
import logging
import pathlib

from .utils import const


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
    ext = "." + filepath.name.split(".")[-1]
    for ft, exts in const.FILETYPES.items():
        if ext in exts:
            return ft
    log.warning(
        "Unable to find a type for file %s, falling back to `plain`.", filepath
    )
    return "plain"
