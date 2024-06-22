#!/usr/bin/env python3
"""Test module testing dotgit.argparser."""

import inspect
import logging
import pathlib

from dotgit_sync import argparser
from dotgit_sync.utils import config as utils
import pytest


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestArgparser:
    """Collection suite to test parsing argument."""

    _foo = "foo"
    _bar = "bar"

    @staticmethod
    def test_no_args() -> None:
        """Test call of parser without args."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set args to default values")

        args = argparser.parser().parse_args([])

        assert args.log_format == "string"
        assert args.verbose == 0
        assert args.source_dir is None
        assert args.source_git is None
        # Bad test as it depends on the location when calling test, but do not
        # now how to make it better
        assert (
            args.config
            == utils.search_git_workdir(pathlib.Path.cwd()) / ".dotgit.yaml"
        )
        assert args.outdir == utils.search_git_workdir(pathlib.Path.cwd())

    def test_args_log_format(self) -> None:
        """Test log format arguments."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set log format")

        args = argparser.parser().parse_args(["-l", self._foo])
        assert args.log_format == self._foo

        args = argparser.parser().parse_args(["--log-format", self._bar])
        assert args.log_format, self._bar

    @staticmethod
    def test_args_verbose() -> None:
        """Test verbosity argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set verbosity level (tested up to 5)")

        for nb_v in range(1, 5):
            log.debug("Testing with %s short and long verbosity args", nb_v)
            verbosity = "v" * nb_v
            args = argparser.parser().parse_args([f"-{verbosity}"])
            assert args.verbose == nb_v

            verbosity = ["--verbose"] * nb_v
            args = argparser.parser().parse_args(verbosity)
            assert args.verbose == nb_v

    @staticmethod
    def test_args_config() -> None:
        """Test config argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set configuration file string")

        fake_cfg_path = str(
            pathlib.Path(__file__).parent / "fake_config" / "empty.dotgit.yaml"
        )
        args = argparser.parser().parse_args(["-c", fake_cfg_path])
        assert str(args.config) == fake_cfg_path

        args = argparser.parser().parse_args(["--config", fake_cfg_path])
        assert str(args.config) == fake_cfg_path

    @staticmethod
    def test_args_outdir() -> None:
        """Test output directory argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set output directory string")

        fake_outdir_path = str(pathlib.Path(__file__).parent / "fake_repo")
        args = argparser.parser().parse_args(["-o", fake_outdir_path])
        assert str(args.outdir) == fake_outdir_path

        args = argparser.parser().parse_args(["--outdir", fake_outdir_path])
        assert str(args.outdir) == fake_outdir_path

    def test_args_source_dir(self) -> None:
        """Test source dir argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set source directory")

        args = argparser.parser().parse_args(["-d", self._foo])
        assert args.source_dir == self._foo

        args = argparser.parser().parse_args(["--source-dir", self._bar])
        assert args.source_dir == self._bar

    def test_args_git_dir(self) -> None:
        """Test git dir argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set source directory")

        args = argparser.parser().parse_args(["-g", self._foo])
        assert args.source_git == self._foo

        args = argparser.parser().parse_args(["--source-git", self._bar])
        assert args.source_git == self._bar

    def test_exclusive_args_source_dir_and_git_dir(self) -> None:
        """Test using both git dir and source dir."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Raise a SystemExit since as -d and -g are mutually exclusive")

        with pytest.raises(SystemExit):
            argparser.parser().parse_args(["-g", self._foo, "-d", self._bar])

        with pytest.raises(SystemExit):
            argparser.parser().parse_args([
                "--source-git",
                self._foo,
                "--source-dir",
                self._bar,
            ])

    @staticmethod
    def test_wrong_args() -> None:
        """Test using wrong argument."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Raise a SystemExit since --foo are not defined")

        with pytest.raises(SystemExit):
            argparser.parser().parse_args(["--foo"])
