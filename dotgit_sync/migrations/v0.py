#!/usr/bin/env python3
"""Configuration file migration."""

import inspect
import logging
import pathlib

from ..utils import const


_TO = "v0"

log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def up(config: dict) -> None:
    """Upgrade from missing `version` to `version: v0`."""
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Process migration v0")

    # Update version to latest
    config[const.VERSION] = _TO
