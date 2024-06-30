#!/usr/bin/env python3
"""Generate licences files."""

import inspect
import logging
import os
import pathlib

from . import render
from .utils import const, templates as utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_LICENSE = "LICENSE"
_COPYRIGHT = "COPYRIGHT"


def _render_license(
    config: dict, dirs: os.path, license_name: str, is_primary: bool = False
) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.template_exists(license_name, dirs)

    if tpl_src is None:
        error_msg = f"There are not template license {license_name}"
        raise FileNotFoundError(error_msg)

    if config[const.LICENSES][const.PRIMARY] == _COPYRIGHT and (
        const.SECONDARIES in config[const.LICENSES]
        and len(config[const.LICENSES][const.SECONDARIES]) >= 0
    ):
        error_msg = (
            f"There can't be a licenses {_COPYRIGHT} and a secondary license"
        )
        raise ValueError(error_msg)

    if is_primary:
        if config[const.LICENSES][const.PRIMARY] == _COPYRIGHT:
            dest = pathlib.Path(config[const.OUTDIR]) / _COPYRIGHT
        else:
            dest = pathlib.Path(config[const.OUTDIR]) / _LICENSE
    else:
        dest = (
            pathlib.Path(config[const.OUTDIR])
            / f"{_LICENSE}.{pathlib.Path(tpl_src).name}"
        )

    content = pathlib.Path(tpl_src).read_text(encoding="utf-8")

    log.info("Render license %s", license_name)
    render.render_file(
        config,
        dest,
        content,
        const.LICENSES,
        tpl_dir=pathlib.Path(tpl_src).parent,
        is_static=False,
    )


def process(config: dict) -> None:
    """Process the generation of all licences files.

    Args:
        config: Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.get_template_dir(config, const.LICENSES)
    try:
        _render_license(
            config, tpl_src, config[const.LICENSES][const.PRIMARY], True
        )
    except FileNotFoundError as error:
        log.warning(error)
        return

    if const.SECONDARIES in config[const.LICENSES]:
        for license_name in config[const.LICENSES][const.SECONDARIES]:
            try:
                _render_license(config, tpl_src, license_name)
            except FileNotFoundError as error:
                log.warning(error)
