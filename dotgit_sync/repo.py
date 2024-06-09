#!/usr/bin/env python3

import argparse
import datetime
import errno
import importlib
import inspect
import logging
import os
import sys

import git
from pykwalify import core, errors

from . import const, utils


log = logging.getLogger(f"{const.PKG_NAME}")
_LOG_TRACE = f"{os.path.basename(__file__)}:{__name__}"

DATE = "date"
FIRST_YEAR = "first_year"
CURR_YEAR = "current_year"
WORKDIR = "workdir"


def _get_schema_files() -> list:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    schemas = []
    schemas_dir = os.path.join(importlib.resources.files(), "schemas")
    for file in os.listdir(schemas_dir):
        schemas += [os.path.join(schemas_dir, file)]
    return schemas


def _validate_config(config_file: os.path) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    try:
        data = core.Core(
            source_file=config_file, schema_files=_get_schema_files()
        ).validate(raise_exception=True)
        return data
    except errors.SchemaError as error:
        log.error(error.msg)
        sys.exit(errno.ENOENT)
    except FileNotFoundError as error:
        log.error("%s %s", error.strerror, error.filename)
        sys.exit(errno.ENOENT)


def _is_git_repo(path: os.path) -> git.Repo:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    try:
        repo = git.Repo(path=path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError as error:
        log.error("Not in a git repository: %s", error)
        sys.exit(1)
    return repo


def _get_first_commit(
    repo: git.Repo, branch: str = "main", datefmt: str = "%Y"
) -> str:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    commit = list(repo.iter_commits(branch, reverse=True))[0]
    return commit.committed_datetime.strftime(datefmt)


def get_git_dir(path: os.path) -> os.path:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    repo = _is_git_repo(path)
    return os.path.dirname(repo.git_dir)


def get_config(path: os.path, args: argparse.ArgumentParser) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    repo = _is_git_repo(path)

    if args.config:
        config_file_path = os.path.join(os.getcwd(), args.config)
    else:
        config_file_path = os.path.join(repo.working_dir, ".dotgit.yaml")

    config = _validate_config(config_file_path)
    config = utils.merge_json_dict(const.DOTGIT, config)
    config[DATE] = {}
    config[DATE][FIRST_YEAR] = _get_first_commit(repo)
    config[DATE][CURR_YEAR] = datetime.datetime.now().strftime("%Y")
    config[WORKDIR] = repo.working_dir
    return config
