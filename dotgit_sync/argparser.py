#!/usr/bin/env python3

import argparse
import logging

from . import const


CONFIG_FILENAME = ".config.yaml"

log = logging.getLogger(f"{const.PKG_NAME}")


def parse_args() -> argparse.ArgumentParser:
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
More '-v' means more verbosity (up to 3).
Default set to ERROR, then WARNING, INFO, DEBUG.
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
Path to the configuration file. If not specified, will search look at the root
of the git repository.
""",
        nargs="?",
        type=str,
        default=None,
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

    args = parser.parse_args()

    return args
