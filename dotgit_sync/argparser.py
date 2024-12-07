#!/usr/bin/env python3
"""Parse argument provided by users."""

import argparse
import logging
import pathlib

from .utils import config as utils, const


log = logging.getLogger(const.PKG_NAME)


def parser() -> argparse.ArgumentParser:
    """Parser argument which set dotgit sync options."""
    parser = argparse.ArgumentParser(
        prog="dotgit-sync",
        description="""\
Synchronize files from templates based pre repo-configuration. Allowing to
manage usual common repo files (such as linter, licenses, etc) across multiple
repos
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="""\
Increase default verbosity of the programs.
More '-v' means more verbosity (up to 2).
Default set to WARNING, then INFO, DEBUG.
""",
        action="count",
        default=0,
    )

    parser.add_argument(
        "-l",
        "--log-format",
        help="""\
Output format of the log (either string or json), default is set to 'string'
""",
        type=str,
        nargs="?",
        default="string",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="""\
Path to the configuration file.
If not specified, will search the root of the git repository from current
location.
""",
        type=pathlib.Path,
        nargs="?",
        default=utils.search_git_workdir(pathlib.Path.cwd()) / ".dotgit.yaml",
    )

    parser.add_argument(
        "--migrate",
        help="""\
Run migrations to upgrade .dotgit.yaml configuration file.
""",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    parser.add_argument(
        "-o",
        "--outdir",
        help="""\
Path where the rendered directories and files will be written.
If not specified, will search the root of the git repository from current path.
""",
        type=pathlib.Path,
        nargs="?",
        default=utils.search_git_workdir(pathlib.Path.cwd()),
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-d",
        "--source-dir",
        help="""\
Path to a directory containing templates.
""",
        nargs="?",
        type=str,
        default=None,
    )

    group.add_argument(
        "-g",
        "--source-git",
        help="""\
Path to a git repository containing templates.
""",
        nargs="?",
        type=str,
        default=None,
    )

    return parser
