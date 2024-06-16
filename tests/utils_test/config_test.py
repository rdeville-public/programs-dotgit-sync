#!/usr/bin/env python3

import datetime
import errno
import inspect
import logging
import os
import pathlib
import shutil

from dotgit_sync import argparser
from dotgit_sync.utils import config as utils, const
import pytest
import yaml


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestUtilsConfig:
    _script_path = pathlib.Path(__file__).parent
    _output_dir = pathlib.Path(_script_path).parent / "fake_repo"
    _config_dir = pathlib.Path(_script_path).parent / "fake_config"
    _config_file = _config_dir / "valid.with_source_path.dotgit.yaml"
    _config_licenses = {
        "copyright": {
            "email": "mail@domain.tld",
            "owner": "Full Name",
        },
        const.DATE: {
            const.CURR_YEAR: datetime.datetime.now(
                tz=datetime.timezone.utc
            ).strftime("%Y"),
            const.FIRST_YEAR: "1970",
        },
        const.PRIMARY: "MIT",
    }
    _config_licenses_with_curr_date = {
        const.LICENSES: _config_licenses
        | {
            const.DATE: {
                const.CURR_YEAR: "2100",
                const.FIRST_YEAR: "1970",
            },
        },
    }
    _config_maintainers = [
        {
            "mail": "mail@domain.tld",
            "name": "Full Name",
        },
    ]
    _config_name = "Program Name"
    _config_desc = "Program description"
    _config_outdir = {
        const.OUTDIR: _output_dir,
    }
    _config_common = {
        const.LICENSES: _config_licenses,
        "maintainers": _config_maintainers,
        "name": _config_name,
        "description": _config_desc,
    }
    _args = None

    @pytest.fixture(autouse=True)
    def _prepare_fake_repo(self):
        for node in os.listdir(self._output_dir):
            node_path = pathlib.Path(self._output_dir) / node
            if node_path.is_dir():
                shutil.rmtree(node_path)
            elif node_path.is_file() and node_path.name != ".gitkeep":
                node_path.unlink()
        (pathlib.Path(self._output_dir) / ".git").mkdir()
        shutil.copy(
            self._config_dir / "valid.with_source_path.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        self._args = argparser.parser().parse_args([])

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_config_file_not_exists(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should throw an error and exit as config file does not exists"
        )
        cfg_path = self._script_path / "foo.yaml"
        with pytest.raises(SystemExit) as exit_code:
            utils._validate_config(cfg_path)
        error_msg = f"Provided source_file do not exists on disk: {cfg_path}"
        assert error_msg in self._caplog.text
        assert exit_code.value.code == errno.ENOENT

    def test_config_file_empty(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should throw an error and exit as config file does not exists"
        )
        cfg_path = self._config_dir / "empty.dotgit.yaml"
        with pytest.raises(SystemExit) as exit_code:
            utils._validate_config(cfg_path)
        error_msg = "No source file/data was loaded"
        assert error_msg in self._caplog.text
        assert exit_code.value.code == errno.ENODATA

    def test_config_file_schema_not_respected(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error and exit as config file is invalid")
        cfg_path = self._config_dir / "wrong.dotgit.yaml"
        with pytest.raises(SystemExit) as exit_code:
            utils._validate_config(cfg_path)
        error_msg = "[\"Cannot find required key 'maintainers'. Path: ''\"]"
        assert error_msg in self._caplog.text
        assert exit_code.value.code == errno.ENODATA

    def test_config_file_schema_respected(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the configuration read from the config file")
        cfg_path = self._config_dir / "valid.minimal.dotgit.yaml"
        assert utils._validate_config(cfg_path) == yaml.safe_load(
            cfg_path.read_text()
        )

    def test_search_found_git_parent(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the configuration read from the config file")
        fake_cwd_path = self._output_dir / "fake_dir"
        fake_cwd_path.mkdir()
        assert utils.search_git_workdir(fake_cwd_path) == self._output_dir

    def test_search_no_found_git_parent(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as unable to find git parent")
        fake_cwd_path = pathlib.Path("/")
        with pytest.raises(FileNotFoundError) as error:
            utils.search_git_workdir(fake_cwd_path)
        error_msg = (
            "Unable to find any `.git` repository amont parent from "
            + str(fake_cwd_path)
        )
        assert error.match(error_msg)

    def test_get_config_no_args_no_config_file(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as unable to find config file")
        os.chdir(self._output_dir)
        self._args = argparser.parser().parse_args([])
        cfg_path = self._output_dir / ".dotgit.yaml"
        cfg_path.unlink()
        with pytest.raises(SystemExit) as exit_code:
            utils.get_config(self._args)
        error_msg = f"Provided source_file do not exists on disk: {cfg_path}"
        assert error_msg in self._caplog.text
        assert exit_code.value.code == errno.ENOENT

    def test_get_config_no_args_config_file(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the content of configuration files")
        os.chdir(self._output_dir)
        self._args = argparser.parser().parse_args([])
        target_config = (
            {
                const.PKG_NAME: {
                    const.SOURCE: {const.PATH: "../fake_templates"},
                },
            }
            | self._config_common
            | self._config_outdir
        )
        assert utils.get_config(self._args) == target_config

    def test_get_config_args_absolute_config_file(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the content of configuration")
        os.chdir(self._output_dir)
        self._args = argparser.parser().parse_args([
            "-c",
            str(self._config_file),
        ])
        target_config = (
            {
                const.PKG_NAME: {
                    const.SOURCE: {const.PATH: "../fake_templates"},
                },
            }
            | self._config_common
            | self._config_outdir
        )
        assert utils.get_config(self._args) == target_config

    def test_get_config_args_relative_config_file(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the content of configuration")
        # Fake path to dotgit config relative to self._output_dir
        cfg_path = "../fake_config/valid.with_source_path.dotgit.yaml"
        os.chdir(self._output_dir)
        self._args = argparser.parser().parse_args(["-c", str(cfg_path)])
        target_config = (
            {
                const.PKG_NAME: {
                    const.SOURCE: {const.PATH: "../fake_templates"},
                },
            }
            | self._config_common
            | self._config_outdir
        )
        assert utils.get_config(self._args) == target_config

    def test_get_config_args_source_dir(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the content of configuration with source path")
        os.chdir(self._output_dir)
        tpl_path = pathlib.Path.cwd() / ".." / "fake_templates"
        shutil.copy(
            self._config_dir / "valid.minimal.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        self._args = argparser.parser().parse_args(["-d", str(tpl_path)])
        target_config = (
            {
                const.PKG_NAME: {
                    const.SOURCE: {
                        const.PATH: tpl_path,
                    },
                },
            }
            | self._config_common
            | self._config_outdir
            | self._config_licenses_with_curr_date
        )
        assert utils.get_config(self._args) == target_config

    def test_get_config_args_source_git(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the content of configuration with source git")
        os.chdir(self._output_dir)
        tpl_path = pathlib.Path.cwd() / ".." / "fake_templates"
        shutil.copy(
            self._config_dir / "valid.minimal.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        self._args = argparser.parser().parse_args(["-g", str(tpl_path)])
        target_config = (
            {
                const.PKG_NAME: {
                    const.SOURCE: {
                        const.GIT: {
                            const.URL: str(tpl_path),
                        },
                    },
                },
            }
            | self._config_common
            | self._config_outdir
            | self._config_licenses_with_curr_date
        )
        assert utils.get_config(self._args) == target_config

    def test_get_config_args_both_source_git_and_dir(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as both source are defined in config")
        os.chdir(self._output_dir)
        shutil.copy(
            self._config_dir / "wrong.with_both_source.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )

        with pytest.raises(ValueError) as error:
            utils.get_config(self._args)
        git_config = f"{const.PKG_NAME}/{const.SOURCE}/{const.GIT}"
        path_config = f"{const.PKG_NAME}/{const.SOURCE}/{const.PATH}"
        error_msg = (
            f"Path {git_config} and {path_config} in config or as "
            + "args can't be used together."
        )
        assert error.match(error_msg)

    def test_get_config_no_args_no_source(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as no source are defined")
        os.chdir(self._output_dir)
        shutil.copy(
            self._config_dir / "valid.minimal.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        with pytest.raises(ValueError) as error:
            utils.get_config(self._args)
        error_msg = (
            "A source must be specified, either in config file or using args"
        )
        assert error.match(error_msg)

    def test_get_config_wrong_yaml_merge(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as YAML merge config is wrong")
        os.chdir(self._output_dir)
        tpl_path = pathlib.Path.cwd() / ".." / "fake_templates"
        shutil.copy(
            self._config_dir / "wrong.yaml_merge.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        self._args = argparser.parser().parse_args(["-d", str(tpl_path)])
        with pytest.raises(KeyError) as error:
            utils.get_config(self._args)
        error_msg = (
            "In your config file, if path "
            + f"/config/{const.YAML}/{const.MERGE} is set to "
            + f"'{const.ONLY}', key '{const.ONLY}' with a list of "
            + "filename must be present"
        )
        assert error.match(error_msg)
