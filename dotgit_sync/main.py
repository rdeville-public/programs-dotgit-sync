#!/usr/bin/env python
"""Entrypoint of Dotgit Sync."""

import argparse
import inspect
import logging
import pathlib
import sys

import json5
import requests
import yaml

from . import (
    argparser,
    filetype,
    gitignore,
    licenses,
    logger,
    render,
)
from .utils import config as cfg_utils, const, templates as tpl_utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def _process_file(
    config: dict, dst: str, sources: list[str], ft: str, is_static: bool = True
) -> None:
    content = ""
    for src in sources:
        content += pathlib.Path(src).read_text(encoding="utf-8")
    render.render_file(config, dst, content, ft, is_static=is_static)


def _process_json(dst: str, sources: list[str], is_yaml: bool = False) -> None:
    content = None
    for src in sources:
        with pathlib.Path(src).open(encoding="utf-8") as file:
            content = yaml.safe_load(file) if is_yaml else json5.load(file)
        render.render_json(dst, content, is_yaml)


def process(config: dict, tpl_dir: str, is_static: bool = False) -> None:
    """Start the process of rendering files.

    Args:
        config: Dotgit Sync configuration
        tpl_dir: Name of the directory of template for rendering
        is_static: Boolean to specify if rendering statics files or not
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    processed = {}
    tpl_utils.compute_template_files(config, tpl_dir, processed)

    for dst, sources in processed.items():
        ft = filetype.get_filetype(sources[0])
        dst_path = pathlib.Path(config[const.OUTDIR]) / dst
        if ft == "json":
            _process_json(dst_path, sources)
        elif (
            ft == "yaml"
            and const.YAML in config[const.PKG_NAME]
            and const.MERGE in config[const.PKG_NAME][const.YAML]
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ALL
        ):
            _process_json(dst_path, sources, True)
        elif (
            ft == "yaml"
            and const.YAML in config[const.PKG_NAME]
            and const.MERGE in config[const.PKG_NAME][const.YAML]
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ONLY
        ):
            if dst_path.name in config[const.PKG_NAME][const.YAML][const.ONLY]:
                _process_json(dst_path, sources, is_yaml=True)
            else:
                _process_file(
                    config, dst_path, sources, ft, is_static=is_static
                )
        else:
            _process_file(config, dst_path, sources, ft, is_static=is_static)


def main(args: argparse.Namespace = sys.argv[1:]) -> None:
    """Entrypoint method of the main module."""
    args = argparser.parser().parse_args(args)
    logger.init_logger(args, log)
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config = cfg_utils.get_config(args)

    if const.GIT in config[const.PKG_NAME][const.SOURCE]:  # pragma: no cover
        tpl_utils.clone_template_repo(config)

    licenses.process(config)
    try:
        gitignore.process(config)
    except requests.exceptions.ConnectionError as error:  # pragma: no cover
        log.warning(error)

    process(config, "statics", is_static=True)
    process(config, "templates")


if __name__ == "__main__":  # pragma: no cover
    main()
