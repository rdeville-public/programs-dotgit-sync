#!/usr/bin/env python3

import datetime
import errno
import importlib
import inspect
import logging
import os
import sys

import git
import pykwalify

import const

DATE = "date"
FIRST_YEAR = "first_year"
CURR_YEAR = "current_year"
WORKDIR = "workdir"

log = logging.getLogger(f"{const.PKG_NAME}")


def _get_schema_files() -> list:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    schemas = []
    for file in importlib.resources.files("schemas").iterdir():
        schemas += [str(file)]
    return schemas


def _validate_config(config_file: os.path) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    try:
        print(_get_schema_files())
        data = pykwalify.core.Core(
            source_file=config_file, schema_files=_get_schema_files()
        ).validate(raise_exception=True)
        return data
    except pykwalify.errors.SchemaError as error:
        log.error(error.msg)
        sys.exit(errno.ENOENT)
    except FileNotFoundError as error:
        log.error("%s %s", error.strerror, error.filename)
        sys.exit(errno.ENOENT)


def _is_git_repo(path: os.path) -> git.Repo:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    try:
        repo = git.Repo(path=path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError as error:
        log.error("Not in a git repository: %s", error)
        sys.exit(1)
    return repo


def _get_first_commit(repo: git.Repo, branch: str = "main", datefmt: str = "%Y") -> str:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    commit = list(repo.iter_commits(branch, reverse=True))[0]
    return commit.committed_datetime.strftime(datefmt)


def get_git_dir(path: os.path) -> os.path:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    repo = _is_git_repo(path)
    return os.path.dirname(repo.git_dir)


def get_config(path: os.path) -> dict:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    repo = _is_git_repo(path)
    config_file_path = os.path.join(repo.working_dir, ".config.yaml")
    config = _validate_config(config_file_path)
    config[DATE] = {}
    config[DATE][FIRST_YEAR] = _get_first_commit(repo)
    config[DATE][CURR_YEAR] = datetime.datetime.now().strftime("%Y")
    config[WORKDIR] = repo.working_dir
    return config
