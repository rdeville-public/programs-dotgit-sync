#!/usr/bin/env python3
"""Configuration file migration."""

import inspect
import logging
import pathlib

from ..utils import const


_FROM = "v0"
_TO = "v1alpha1"

log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def up(config: dict) -> dict:
    """Upgrade from missing `v0` to `v1alpha1`."""
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Process migration %s to %s", _FROM, _TO)

    # Update maintainer key
    new = {}
    for maintainer in config[const.MAINTAINERS]:
        new[maintainer[const.NAME]] = maintainer[const.MAIL]
    config[const.MAINTAINERS] = new

    # Update licenses.copyright key
    new = {
        config[const.LICENSES][const.COPYRIGHT][const.OWNER]: config[
            const.LICENSES
        ][const.COPYRIGHT][const.EMAIL]
    }
    config[const.LICENSES][const.COPYRIGHT] = new

    # Move content of statics into templates
    new = config[const.STATICS]
    for template in new:
        if template not in config[const.TEMPLATES]:
            config[const.TEMPLATES].append(template)

    del config[const.STATICS]

    # Update version to latest
    config[const.VERSION] = _TO

    return config
