#!/usr/bin/env python

import inspect
import logging
import os

import json5
import pylibmagic  # noqa: F401
import requests
import yaml

from . import (
    argparser,
    const,
    filetype,
    gitignore,
    licenses,
    logger,
    render,
    repo,
    utils,
)


log = logging.getLogger(f"{const.PKG_NAME}")
_LOG_TRACE = f"{os.path.basename(__file__)}:{__name__}"


def _process_file(
    config: dict, dst: str, sources: list[str], ft: str, is_static: bool = True
) -> None:
    content = ""
    for src in sources:
        with open(src, encoding="utf-8") as file:
            content += file.read()
    render.render_file(config, dst, content, ft, is_static=is_static)


def _process_json(
    config: dict, dst: str, sources: list[str], is_yaml: bool = False
) -> None:
    content = None
    for src in sources:
        with open(src, encoding="utf-8") as file:
            if is_yaml:
                content = yaml.safe_load(file)
            else:
                content = json5.load(file)
        render.render_json(config, dst, content, is_yaml)


def process(config: dict, tpl_type: str, is_static: bool = False) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    processed = {}
    utils.compute_template_files(config, tpl_type, processed)

    for dst, sources in processed.items():
        ft = filetype.get_filetype(sources[0])
        dst = os.path.join(config["git_root"], dst)
        if ft == "json":
            _process_json(config, dst, sources)
        elif (
            ft == "yaml"
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ALL
        ):
            _process_json(config, dst, sources, True)
        elif (
            ft == "yaml"
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ONLY
        ):
            if const.ONLY not in config[const.PKG_NAME][const.YAML]:
                raise KeyError(
                    "In your config file, if path "
                    + f"/config/{const.YAML}/{const.MERGE} is set to "
                    + f"'{const.ONLY}', key '{const.ONLY}' with a list of "
                    + "filename must be present"
                )

            if (
                os.path.basename(dst)
                in config[const.PKG_NAME][const.YAML][const.ONLY]
            ):
                _process_json(config, dst, sources, is_yaml=True)
            else:
                _process_file(config, dst, sources, ft, is_static=is_static)
        else:
            _process_file(config, dst, sources, ft, is_static=is_static)


def main():
    args = argparser.parse_args()
    logger.init_logger(args, log)
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config = repo.get_config(os.getcwd(), args)
    config["git_root"] = repo.get_git_dir(os.getcwd())

    # Git or Path config passed as args override .config.yaml
    if "source" not in config:
        config["source"] = {}

    if args.source_git:
        config["source"]["git"] = {}
        config["source"]["git"]["url"] = args.source_git
    elif args.source_dir:
        config["source"]["path"] = os.path.join(os.getcwd(), args.source_dir)

    if "git" in config["source"] and "path" in config["source"]:
        raise ValueError(
            "`source.git` and `source.path` in config can't be used together!"
        )

    if "git" in config["source"]:
        utils.clone_template_repo(config)

    licenses.process(config)
    try:
        gitignore.process(config)
    except requests.exceptions.ConnectionError as error:
        log.warning(error)

    process(config, "statics", is_static=True)
    process(config, "templates")


if __name__ == "__main__":
    main()
