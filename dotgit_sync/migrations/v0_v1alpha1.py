#!/usr/bin/env python3
"""Configuration file migration"""

import inspect
import pathlib
import logging

from ..utils import const

_FROM = "v0"
_TO = "v1alpha1"

log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def up(config: dict) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    """Upgrade from missing `v0` to `v1alpha1`"""

    log.info(f"Process migration {_FROM} to {_TO}")

    # Update maintainer key
    new = {}
    for maintainer in config[const.MAINTAINERS]:
        new[maintainer[const.NAME]] = maintainer[const.MAIL]
    config[const.MAINTAINERS] = new

    # Update licenses.copyright key
    new = {
        config[const.LICENSES][const.COPYRIGHT][const.OWNER]:
        config[const.LICENSES][const.COPYRIGHT][const.EMAIL]
    }
    config[const.LICENSES][const.COPYRIGHT] = new

    # Move content of statics into templates
    new = config[const.STATICS]
    for template in new:
        if template not in config[const.TEMPLATES]:
            config[const.TEMPLATES].append(template)

    # Update version to latest
    config[const.VERSION] = _TO
