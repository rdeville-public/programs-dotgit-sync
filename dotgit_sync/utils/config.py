#!/usr/bin/env python3

import argparse
import datetime
import errno
import inspect
import logging
import os
import pathlib
import sys

from pykwalify import core, errors

from . import const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def _get_schema_files() -> list:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    schemas = []
    schemas_dir = pathlib.Path(__file__).parent.parent / "schemas"
    for file in os.listdir(schemas_dir):
        schemas += [str(pathlib.Path(schemas_dir) / file)]
    return schemas


def _validate_config(config_file: pathlib.Path) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    try:
        return core.Core(
            source_file=str(config_file), schema_files=_get_schema_files()
        ).validate(raise_exception=True)

    except errors.SchemaError as error:
        log.exception(error.msg)
        sys.exit(errno.ENODATA)
    except errors.CoreError as error:
        log.exception(error.msg)
        if "No source file/data was loaded" in error.msg:
            sys.exit(errno.ENODATA)
        else:
            sys.exit(errno.ENOENT)


def search_git_workdir(path: pathlib.Path) -> pathlib.Path:
    """Return python git root directory.

    Args:
        path: Path to check if is a git directory

    Return:
        Root git directory
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    current_path = path

    while current_path != pathlib.Path("/"):
        if ".git" in os.listdir(current_path):
            return current_path
        current_path = current_path.parent

    # Do not test "/.git" as it is, to my knowledge, impossible and if possible,
    # consider it a bad thing !

    error_msg = f"Unable to find any `.git` repository amont parent from {path}"
    raise FileNotFoundError(error_msg)


def get_config(args: argparse.ArgumentParser) -> dict:
    """Gather Dotgit Sync configuration from file and args and return it.

    Args:
        path: Path destination where to render dotgit files
        args: User arguments passed to Dotgit Sync

    Return:
        Dictionnary containing Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config = _validate_config(args.config)

    if const.PKG_NAME not in config:
        config[const.PKG_NAME] = {}

    # Git or Path config passed as args override .config.yaml
    if (
        const.SOURCE not in config[const.PKG_NAME]
        and (args.source_git or args.source_dir)
    ) or (args.source_git or args.source_dir):
        config[const.PKG_NAME][const.SOURCE] = {}

        # Args override config in .dotgit.yaml
        if args.source_git:
            config[const.PKG_NAME][const.SOURCE][const.GIT] = {}
            config[const.PKG_NAME][const.SOURCE][const.GIT][const.URL] = (
                args.source_git
            )

        if args.source_dir:
            config[const.PKG_NAME][const.SOURCE][const.PATH] = (
                pathlib.Path(pathlib.Path.cwd()) / args.source_dir
            )

    if const.SOURCE not in config[const.PKG_NAME]:
        error_msg = (
            "A source must be specified, either in config file or using args"
        )
        raise ValueError(error_msg)

    if (
        const.GIT in config[const.PKG_NAME][const.SOURCE]
        and const.PATH in config[const.PKG_NAME][const.SOURCE]
    ):
        git_config = f"{const.PKG_NAME}/{const.SOURCE}/{const.GIT}"
        path_config = f"{const.PKG_NAME}/{const.SOURCE}/{const.PATH}"
        error_msg = (
            f"Path {git_config} and {path_config} in config or as "
            + "args can't be used together."
        )
        raise ValueError(error_msg)

    if (
        const.YAML in config[const.PKG_NAME]
        and const.MERGE in config[const.PKG_NAME][const.YAML]
        and config[const.PKG_NAME][const.YAML][const.MERGE] == const.ONLY
        and const.ONLY not in config[const.PKG_NAME][const.YAML]
    ):
        error_msg = (
            "In your config file, if path "
            + f"/config/{const.YAML}/{const.MERGE} is set to "
            + f"'{const.ONLY}', key '{const.ONLY}' with a list of "
            + "filename must be present"
        )
        raise KeyError(error_msg)

    config[const.OUTDIR] = args.outdir
    if const.CURR_YEAR not in config[const.LICENSES][const.DATE]:
        config[const.LICENSES][const.DATE][const.CURR_YEAR] = (
            datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y")
        )

    return config
