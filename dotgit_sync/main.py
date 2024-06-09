#!/usr/bin/env python
"""Entrypoint of Dotgit Sync."""

import inspect
import logging
import pathlib

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


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def _process_file(
    config: dict, dst: str, sources: list[str], ft: str, is_static: bool = True
) -> None:
    content = ""
    for src in sources:
        content += pathlib.Path(src).read_text(encoding="utf-8")
    render.render_file(config, dst, content, ft, is_static=is_static)


def _process_json(
    config: dict, dst: str, sources: list[str], is_yaml: bool = False
) -> None:
    content = None
    for src in sources:
        with pathlib.Path(src).open(encoding="utf-8") as file:
            content = yaml.safe_load(file) if is_yaml else json5.load(file)
        render.render_json(config, dst, content, is_yaml)


def process(config: dict, tpl_dir: str, is_static: bool = False) -> None:
    """Start the process of rendering files.

    Args:
        config: Dotgit Sync configuration
        tpl_dir: Name of the directory of template for rendering
        is_static: Boolean to specify if rendering statics files or not
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    processed = {}
    utils.compute_template_files(config, tpl_dir, processed)

    for dst, sources in processed.items():
        ft = filetype.get_filetype(sources[0])
        dst_path = pathlib.Path(config["git_root"]) / dst
        if ft == "json":
            _process_json(config, dst_path, sources)
        elif (
            ft == "yaml"
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ALL
        ):
            _process_json(config, dst_path, sources, True)
        elif (
            ft == "yaml"
            and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ONLY
        ):
            if const.ONLY not in config[const.PKG_NAME][const.YAML]:
                error_msg = (
                    "In your config file, if path "
                    + f"/config/{const.YAML}/{const.MERGE} is set to "
                    + f"'{const.ONLY}', key '{const.ONLY}' with a list of "
                    + "filename must be present"
                )
                raise KeyError(error_msg)

            if (
                pathlib.Path(dst_path).name
                in config[const.PKG_NAME][const.YAML][const.ONLY]
            ):
                _process_json(config, dst_path, sources, is_yaml=True)
            else:
                _process_file(
                    config, dst_path, sources, ft, is_static=is_static
                )
        else:
            _process_file(config, dst_path, sources, ft, is_static=is_static)


def main() -> None:
    """Entrypoint method of the main module."""
    args = argparser.parse_args()
    logger.init_logger(args, log)
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config = repo.get_config(pathlib.Path.cwd(), args)
    config["git_root"] = repo.get_git_dir(pathlib.Path.cwd())

    # Git or Path config passed as args override .config.yaml
    if "source" not in config:
        config["source"] = {}

    if args.source_git:
        config["source"]["git"] = {}
        config["source"]["git"]["url"] = args.source_git
    elif args.source_dir:
        config["source"]["path"] = (
            pathlib.Path(pathlib.Path.cwd()) / args.source_dir
        )

    if "git" in config["source"] and "path" in config["source"]:
        error_msg = (
            "`source.git` and `source.path` in config can't be used together!"
        )
        raise ValueError(error_msg)

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
