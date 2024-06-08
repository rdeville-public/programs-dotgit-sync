#!/usr/bin/env python3

import inspect
import logging
import os

import const
import render
import repo
import utils

log = logging.getLogger(f"{const.PKG_NAME}")
_LOG_TRACE = f"{os.path.basename(__file__)}:{__name__}"

LICENSES = "licenses"
_MAIN = "main"
_OTHERS = "others"


def _render_license(
    config: dict, dirs: os.path, license_name: str, main: bool = False
) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.template_exists(license_name, dirs)

    if tpl_src is None:
        log.warning("There are not template license %s", license_name)
        return

    if main:
        dest = os.path.join(config[repo.WORKDIR], "LICENSE")
    else:
        dest = os.path.join(
            config[repo.WORKDIR], f"LICENSE.{os.path.basename(tpl_src)}"
        )

    with open(tpl_src, "r", encoding="utf-8") as file:
        content = file.read()

    log.info("Render license %s", license_name)
    render.render_file(
        config,
        dest,
        content,
        "license",
        tpl_dir=os.path.dirname(tpl_src),
        is_static=False,
    )
    return


def process(config: dict) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = utils.get_template_dir(config, LICENSES)
    _render_license(config, tpl_src, config[LICENSES][_MAIN], True)

    if _OTHERS in config[LICENSES]:
        for license_name in config[LICENSES][_OTHERS]:
            _render_license(config, tpl_src, license_name)
