#!/usr/bin/env python3
"""Utility that help managing dotgit configuration."""

import argparse
import datetime
import errno
import inspect
import logging
import os
import pathlib
import sys

from pykwalify import core, errors
import pykwalify

from . import const, migrate_config


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def _get_schema_files() -> list:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    schemas = []
    schemas_dir = pathlib.Path(__file__).parent.parent / "schemas"
    for file in os.listdir(schemas_dir):
        schemas += [str(pathlib.Path(schemas_dir) / file)]
    return schemas


def _validate_config(config: dict) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    try:
        return core.Core(
            source_data=config, schema_files=_get_schema_files()
        ).validate(raise_exception=True)
    except errors.SchemaError as error:
        log.exception(error.msg)
        sys.exit(errno.ENODATA)
    except errors.CoreError as error:
        log.exception(error.msg)
        if "No source file/data was loaded" in str(error.msg):
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


def get_merge_enforce(
    ft: str, config: dict, dst_path: pathlib.Path
) -> tuple[bool, bool]:
    """Return simple dictionnary to check enforce/merge config for json or yaml.

    Simply check configuration for a given key, yaml or json, and return a
    dictionnary of booleans about merging en enforcing policy set in the main
    dotgit config file.

    Args:
      ft: Filetype, either 'yaml' or 'json' are supported
      config: Dictionnary containing Dotgit Sync configuration
      dst_path: Basename of the file output to render

    Return:
      A dictionnary with following structure:

      ```json
      {
        merge: boolean,
        enforce: boolean
      }
      ```

      Where value is 'True' or 'False' is either 'merge' or 'enforce' policy
      should be apply to the file to render.
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    output = {const.ENFORCE: False, const.MERGE: False}

    for config_key in output:
        try:
            method = config[const.DOTGIT][ft][config_key][const.METHOD]
        except KeyError:
            continue
        if (method == const.ALL) or (
            method == const.ONLY
            and dst_path in config[const.DOTGIT][ft][config_key][const.ONLY]
        ):
            output[config_key] = True

    return output[const.MERGE], output[const.ENFORCE]


def get_config(args: argparse.ArgumentParser) -> dict:
    """Gather Dotgit Sync configuration from file and args and return it.

    Args:
        path: Path destination where to render dotgit files
        args: User arguments passed to Dotgit Sync

    Return:
        Dictionnary containing Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    migration_required, config = migrate_config.check_migrations(args)

    if migration_required and not args.migrate:
        log.error(
            f"Migration required from {config[const.VERSION]} to {const.CFG_VERSIONS[-1]}."
        )
        log.error(
            "Use  `--migrate` to update your config file to latest version."
        )
        exit(1)
    elif migration_required and args.migrate:
        migrate_config.process_migration(args, config)

    _validate_config(config)

    if const.DOTGIT not in config:
        config[const.DOTGIT] = {}

    # Git or Path config passed as args override .config.yaml
    if (
        const.SOURCE not in config[const.DOTGIT]
        and (args.source_git or args.source_dir)
    ) or (args.source_git or args.source_dir):
        config[const.DOTGIT][const.SOURCE] = {}

        # Args override config in .dotgit.yaml
        if args.source_git:
            config[const.DOTGIT][const.SOURCE][const.GIT] = {}
            config[const.DOTGIT][const.SOURCE][const.GIT][const.URL] = (
                args.source_git
            )

        if args.source_dir:
            config[const.DOTGIT][const.SOURCE][const.PATH] = (
                pathlib.Path(pathlib.Path.cwd()) / args.source_dir
            )

    if const.SOURCE not in config[const.DOTGIT]:
        error_msg = (
            "A source must be specified, either in config file or using args"
        )
        raise ValueError(error_msg)

    if (
        const.GIT in config[const.DOTGIT][const.SOURCE]
        and const.PATH in config[const.DOTGIT][const.SOURCE]
    ):
        git_config = f"{const.DOTGIT}/{const.SOURCE}/{const.GIT}"
        path_config = f"{const.DOTGIT}/{const.SOURCE}/{const.PATH}"
        error_msg = (
            f"Path {git_config} and {path_config} in config or as "
            + "args can't be used together."
        )
        raise ValueError(error_msg)

    for key in [const.YAML, const.JSON]:
        for subkey in [const.MERGE, const.ENFORCE]:
            if (
                key in config[const.DOTGIT]
                and subkey in config[const.DOTGIT][key]
                and const.METHOD in config[const.DOTGIT][key][subkey]
                and config[const.DOTGIT][key][subkey][const.METHOD]
                == const.ONLY
                and const.ONLY not in config[const.DOTGIT][key][subkey]
            ):
                error_msg = (
                    "In your config file, if path "
                    + f"/config/{key}/{subkey} is set to "
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
