#!/usr/bin/env python

import inspect
import json
import logging
import os

# pylint: disable=W0611
import pylibmagic
import yaml

import argparser
import const
import filetype
import gitignore
import licenses
import logger
import render
import repo
import utils

log = logging.getLogger(f"{const.PKG_NAME}")


def _process_file(
    config: dict, dst: str, sources: list[str], ft: str, is_static: bool = True
) -> None:
    content = ""
    for src in sources:
        with open(src, "r", encoding="utf-8") as file:
            content += file.read()
    render.render_file(config, dst, content, ft, is_static=is_static)


def _process_json(config: dict, dst: str, sources: list[str]) -> None:
    content = None
    for src in sources:
        with open(src, "r", encoding="utf-8") as file:
            content = json.load(file)
        render.render_json(config, dst, content)


def process(config: dict, tpl_type: str, is_static: bool = False) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    processed = {}
    utils.compute_template_files(config, tpl_type, processed)

    for dst, sources in processed.items():
        ft = filetype.get_filetype(sources[0])
        if ft == "json":
            _process_json(config, dst, sources)
        else:
            _process_file(config, dst, sources, ft, is_static=is_static)


def main():
    args = argparser.parse_args()
    logger.init_logger(args, log)
    log.debug("%s", __name__)

    config = repo.get_config(os.getcwd())
    config["git_root"] = repo.get_git_dir(os.getcwd())
    if args.source_git:
        config["source"] = {}
        utils.clone_template_repo(config, args.source_git)
    elif args.source_dir:
        config["source"] = {}
        config["source"]["path"] = os.path.join(os.getcwd(), args.source_dir)
    log.debug(config)

    licenses.process(config)
    gitignore.process(config)
    process(config, "statics", is_static=True)
    process(config, "templates")


if __name__ == "__main__":
    main()
