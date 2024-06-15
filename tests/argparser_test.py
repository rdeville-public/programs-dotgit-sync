#!/usr/bin/env python3

import inspect
import logging
import pathlib
import unittest

from dotgit_sync import argparser
from dotgit_sync.utils import config as utils


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestArgparser(unittest.TestCase):
    _foo = "foo"
    _bar = "bar"

    def test_no_args(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set args to default values")
        args = argparser.parser().parse_args([])
        self.assertEqual(args.log_format, "string")
        self.assertEqual(args.verbose, 0)
        self.assertEqual(args.source_dir, None)
        self.assertEqual(args.source_git, None)
        # Bad test as it depends on the location when calling test, but do not
        # now how to make it better
        self.assertEqual(
            args.config,
            utils.search_git_workdir(pathlib.Path.cwd()) / ".dotgit.yaml",
        )
        self.assertEqual(
            args.outdir, utils.search_git_workdir(pathlib.Path.cwd())
        )

    def test_args_log_format(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set log format")
        args = argparser.parser().parse_args(["-l", self._foo])
        self.assertEqual(args.log_format, self._foo)

        args = argparser.parser().parse_args(["--log-format", self._bar])
        self.assertEqual(args.log_format, self._bar)

    def test_args_verbose(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set verbosity level (tested up to 5)")
        for nb_v in range(1, 5):
            log.debug("Testing with %s short and long verbosity args", nb_v)
            verbosity = "v" * nb_v
            args = argparser.parser().parse_args([f"-{verbosity}"])
            self.assertEqual(args.verbose, nb_v)

            verbosity = ["--verbose"] * nb_v
            args = argparser.parser().parse_args(verbosity)
            self.assertEqual(args.verbose, nb_v)

    def test_args_config(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set configuration file string")
        fake_cfg_path = str(
            pathlib.Path(__file__).parent / "fake_config" / "empty.dotgit.yaml"
        )
        args = argparser.parser().parse_args(["-c", fake_cfg_path])
        self.assertEqual(str(args.config), fake_cfg_path)

        args = argparser.parser().parse_args(["--config", fake_cfg_path])
        self.assertEqual(str(args.config), fake_cfg_path)

    def test_args_outdir(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set output directory string")
        fake_outdir_path = str(pathlib.Path(__file__).parent / "fake_repo")
        args = argparser.parser().parse_args(["-o", fake_outdir_path])
        self.assertEqual(str(args.outdir), fake_outdir_path)

        args = argparser.parser().parse_args(["--outdir", fake_outdir_path])
        self.assertEqual(str(args.outdir), fake_outdir_path)

    def test_args_source_dir(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set source directory")
        args = argparser.parser().parse_args(["-d", self._foo])
        self.assertEqual(args.source_dir, self._foo)

        args = argparser.parser().parse_args(["--source-dir", self._bar])
        self.assertEqual(args.source_dir, self._bar)

    def test_args_git_dir(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set source directory")
        args = argparser.parser().parse_args(["-g", self._foo])
        self.assertEqual(args.source_git, self._foo)

        args = argparser.parser().parse_args(["--source-git", self._bar])
        self.assertEqual(args.source_git, self._bar)

    def test_exclusive_args_source_dir_and_git_dir(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Raise a SystemExit since as -d and -g are mutually exclusive")
        with self.assertRaises(SystemExit):
            argparser.parser().parse_args(["-g", self._foo, "-d", self._bar])

        with self.assertRaises(SystemExit):
            argparser.parser().parse_args([
                "--source-git",
                self._foo,
                "--source-dir",
                self._bar,
            ])

    def test_wrong_args(self) -> None:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Raise a SystemExit since --foo are not defined")
        with self.assertRaises(SystemExit):
            argparser.parser().parse_args(["--foo"])
