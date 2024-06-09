#!/usr/bin/env python3
"""Generate licences files."""

import inspect
import logging
import os
import pathlib

from . import const, render, repo, utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_MAIN = "main"
_OTHERS = "others"
_LICENSE = "LICENSE"


def _render_license(
    config: dict, dirs: os.path, license_name: str, main: bool = False
) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.template_exists(license_name, dirs)

    if tpl_src is None:
        log.warning("There are not template license %s", license_name)
        return

    if main:
        dest = pathlib.Path(config[repo.WORKDIR]) / _LICENSE
    else:
        dest = (
            pathlib.Path(config[repo.WORKDIR])
            / f"{_LICENSE}.{pathlib.Path(tpl_src).name}"
        )

    content = pathlib.Path(tpl_src).read_text(encoding="utf-8")

    log.info("Render license %s", license_name)
    render.render_file(
        config,
        dest,
        content,
        const.LICENSE,
        tpl_dir=pathlib.Path(tpl_src).parent,
        is_static=False,
    )
    return


def process(config: dict) -> None:
    """Process the generation of all licences files.

    Args:
        config: Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.get_template_dir(config, const.LICENSE)
    _render_license(config, tpl_src, config[const.LICENSE][_MAIN], True)

    if _OTHERS in config[const.LICENSE]:
        for license_name in config[const.LICENSE][_OTHERS]:
            _render_license(config, tpl_src, license_name)
