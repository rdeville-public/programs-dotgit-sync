#!/usr/bin/env python3

import inspect
import logging
import os

import const
import render
import repo
import utils

LICENSES = "licenses"
_MAIN = "main"
_OTHERS = "others"

log = logging.getLogger(f"{const.PKG_NAME}")


def _render_license(
    config: dict, dirs: os.path, license_name: str, main: bool = False
) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
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

    log.debug("Render license %s", license_name)
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
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    tpl_src = utils.get_template_dir(config, LICENSES)
    log.debug("Licenses directory hosting template %s", tpl_src)

    _render_license(config, tpl_src, config[LICENSES][_MAIN], True)

    if _OTHERS in config[LICENSES]:
        for license_name in config[LICENSES][_OTHERS]:
            _render_license(config, tpl_src, license_name)
