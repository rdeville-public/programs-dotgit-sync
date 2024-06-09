#!/usr/bin/env python3
"""Module processing with git repo relative method."""

import argparse
import datetime
import errno
import importlib
import inspect
import logging
import os
import pathlib
import sys

import git
from pykwalify import core, errors

from . import const, utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

DATE = "date"
FIRST_YEAR = "first_year"
CURR_YEAR = "current_year"
WORKDIR = "workdir"


def _get_schema_files() -> list:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    schemas = []
    schemas_dir = pathlib.Path(importlib.resources.files()) / "schemas"
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
        sys.exit(errno.ENOENT)
    except FileNotFoundError as error:
        log.exception("%s %s", error.strerror, error.filename)
        sys.exit(errno.ENOENT)


def _is_git_repo(path: pathlib.Path) -> git.Repo:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    try:
        repo = git.Repo(path=path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        log.exception("Not in a git repository")
        sys.exit(1)
    return repo


def _get_first_commit(
    repo: git.Repo, branch: str = "main", datefmt: str = "%Y"
) -> str:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    commit = next(iter(repo.iter_commits(branch, reverse=True)))
    return commit.committed_datetime.strftime(datefmt)


def get_git_dir(path: pathlib.Path) -> pathlib.Path:
    """Return python git root directory.

    Args:
        path: Path to check if is a git directory

    Return:
        Root git directory
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    repo = _is_git_repo(path)
    return pathlib.Path(repo.git_dir).parent


def get_config(path: pathlib.Path, args: argparse.ArgumentParser) -> dict:
    """Gather Dotgit Sync configuration from file and args and return it.

    Args:
        path: Path destination where to render dotgit files
        args: User arguments passed to Dotgit Sync

    Return:
        Dictionnary containing Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    repo = _is_git_repo(path)

    if args.config:
        config_file_path = pathlib.Path(pathlib.Path.cwd()) / args.config
    else:
        config_file_path = pathlib.Path(repo.working_dir) / ".dotgit.yaml"

    config = _validate_config(config_file_path)
    config = utils.merge_json_dict(const.DOTGIT, config)
    config[DATE] = {}
    config[DATE][FIRST_YEAR] = _get_first_commit(repo)
    config[DATE][CURR_YEAR] = datetime.datetime.now(
        tz=datetime.timezone.utc
    ).strftime("%Y")
    config[WORKDIR] = repo.working_dir
    return config
