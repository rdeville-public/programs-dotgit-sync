#!/usr/bin/env python3
"""Module testing dotgit_sync.utils.template."""

import inspect
import logging
import pathlib
import shutil
import tempfile

import dotgit_sync
from dotgit_sync.utils import config as cfg_utils, const, templates as utils
import git
import pytest


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestUtilsTemplate:
    """Collection to test utility related to template."""

    _script_path = pathlib.Path(__file__).parent
    _tpl_dir = _script_path / ".." / "fake_templates"
    _license_tpl_dir = (
        pathlib.Path(dotgit_sync.__file__).parent
        / const.TEMPLATES
        / const.LICENSES
    )

    @pytest.fixture(autouse=True)
    def _inject_fixtures(self, caplog: str) -> None:
        self._caplog = caplog

    def test_get_licenses_template_dir(self) -> None:
        """Test it return the right folder storing licenses."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return path to the licenses templates")

        assert (
            utils.get_template_dir({}, const.LICENSES) == self._license_tpl_dir
        )

    def test_get_template_dir(self) -> None:
        """Test it return the right folder storing statics or templates."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return path to templates and statics folder in source")

        config = {const.PKG_NAME: {const.SOURCE: {const.PATH: self._tpl_dir}}}
        assert (
            utils.get_template_dir(config, const.TEMPLATES)
            == self._tpl_dir / const.TEMPLATES
        )
        assert (
            utils.get_template_dir(config, const.STATICS)
            == self._tpl_dir / const.STATICS
        )

    def test_template_file_exists(self) -> None:
        """Test a template file exists from template flavor and filename."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return path to template file")

        tpl_src = self._tpl_dir / const.STATICS / "all_types"
        filename = "fake.json"
        file_path = tpl_src / filename
        assert utils.template_exists(filename, tpl_src) == file_path

    def test_template_file_not_exists(self) -> None:
        """Test a template file does not exist from template flavor and filename."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return None as template file does not exists")

        tpl_src = self._tpl_dir / const.STATICS / "all_types"
        filename = "fake.fake"
        assert utils.template_exists(filename, tpl_src) is None

    def test_process_dir_template(self) -> None:
        """Test building list of template files from a template flavor."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Return a set of dest files associated with their template sources"
        )

        path = self._tpl_dir / const.TEMPLATES / "few_types"
        process_target = {
            pathlib.Path("fake.toml"): [
                path / "fake.toml",
            ],
            pathlib.Path("folder_cfg/fake.toml"): [
                path / "folder_cfg" / "fake.toml",
            ],
        }
        processed = {}
        utils._process_dir_template(path, "", processed)  # noqa: SLF001
        assert processed == process_target

    def test_compute_template_files(self) -> None:
        """Test building list of template files from multiple template flavors."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Return a set of dest files associated with their template sources"
        )

        path = self._tpl_dir / const.TEMPLATES
        process_target = {
            pathlib.Path("fake.json"): [
                path / "all_types" / "fake.json",
            ],
            pathlib.Path("fake.md"): [
                path / "other_types" / "fake.md",
            ],
            pathlib.Path("fake.toml"): [
                path / "few_types" / "fake.toml",
                path / "other_types" / "fake.toml",
            ],
            pathlib.Path("folder_cfg/fake.toml"): [
                path / "few_types" / "folder_cfg" / "fake.toml",
            ],
        }
        config = {
            const.PKG_NAME: {
                const.SOURCE: {const.PATH: self._tpl_dir},
            },
            const.TEMPLATES: [
                "all_types",
                "few_types",
                "other_types",
            ],
        }
        processed = {}
        utils.compute_template_files(config, const.TEMPLATES, processed)
        assert processed == process_target

    def test_compute_template_files_wrong_dir(self) -> None:
        """Test wrong template flavor provided."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should log a warning that template directory does not exists")

        wrong_dir = "wrong_tpl"
        config = {
            const.PKG_NAME: {
                const.SOURCE: {const.PATH: self._tpl_dir},
            },
            const.TEMPLATES: [
                wrong_dir,
            ],
        }
        processed = {}
        utils.compute_template_files(config, const.TEMPLATES, processed)
        warning_msg = (
            f"Directory '{wrong_dir}' of type '{const.TEMPLATES}' "
            + "is not in template source"
        )
        assert warning_msg in self._caplog.text

    @staticmethod
    def test_simple_cloning_git_repo() -> None:
        """Test cloning repo without ref."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should clone itself in temporary directory")

        repo_dest = tempfile.mkdtemp()
        repo_workdir = cfg_utils.search_git_workdir(
            pathlib.Path(__file__).parent
        )
        repo = git.Repo.clone_from(repo_workdir, repo_dest)
        config = {
            const.PKG_NAME: {
                const.SOURCE: {
                    const.GIT: {const.URL: repo.working_dir},
                },
            },
        }
        utils.clone_template_repo(config)
        cloned_repo = git.Repo(
            pathlib.Path(config[const.PKG_NAME][const.SOURCE][const.PATH])
        )
        assert repo.head.commit == cloned_repo.head.commit
        shutil.rmtree(cloned_repo.working_dir)

    @staticmethod
    def test_ref_cloning_git_repo() -> None:
        """Test cloning repo with a ref."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should clone itself in temporary directory")

        url = "https://framagit.org/rdeville-public/programs/dotgit-sync.git"
        ref = "v0.0.0"

        config = {
            const.PKG_NAME: {
                const.SOURCE: {
                    const.GIT: {const.URL: url, const.REF: ref},
                },
            },
        }
        utils.clone_template_repo(config)
        cloned_repo = git.Repo(
            pathlib.Path(config[const.PKG_NAME][const.SOURCE][const.PATH])
        )
        assert (
            str(cloned_repo.head.commit)
            == "2532876902b28883c6b0f736453f61a712f6d97b"
        )
        shutil.rmtree(cloned_repo.working_dir)
