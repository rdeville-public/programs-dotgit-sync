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

        config = {const.DOTGIT: {const.SOURCE: {const.PATH: self._tpl_dir}}}
        assert (
            utils.get_template_dir(config, const.TEMPLATES)
            == self._tpl_dir / const.TEMPLATES
        )

    def test_process_dir_template(self) -> None:
        """Test building list of template files from a template flavor."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Return a set of dest files associated with their template sources"
        )

        path = self._tpl_dir / const.TEMPLATES / "few_types"
        process_target = {
            pathlib.Path("fake.toml"): [
                (path / "fake.toml").resolve(),
            ],
            pathlib.Path("folder_cfg/fake.toml"): [
                (path / "folder_cfg" / "fake.toml").resolve(),
            ],
            pathlib.Path("fake.md"): [
                (path / "fake.md").resolve(),
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
            pathlib.Path(".editorconfig"): [
                pathlib.Path(path / "all_types" / ".editorconfig").resolve(),
            ],
            pathlib.Path(".envrc"): [
                pathlib.Path(path / "all_types" / ".envrc").resolve(),
            ],
            pathlib.Path(".gitignore"): [
                pathlib.Path(path / "all_types" / ".gitignore").resolve(),
            ],
            pathlib.Path(".yamllint"): [
                pathlib.Path(path / "all_types" / ".yamllint").resolve(),
            ],
            pathlib.Path(".yamlignore"): [
                pathlib.Path(path / "all_types" / ".yamlignore").resolve(),
            ],
            pathlib.Path("fake.bash"): [
                pathlib.Path(path / "all_types" / "fake.bash").resolve(),
            ],
            pathlib.Path("fake.hbs"): [
                pathlib.Path(path / "all_types" / "fake.hbs").resolve(),
            ],
            pathlib.Path("fake.in"): [
                pathlib.Path(path / "all_types" / "fake.in").resolve(),
            ],
            pathlib.Path("fake.j2"): [
                pathlib.Path(path / "all_types" / "fake.j2").resolve(),
            ],
            pathlib.Path("fake.js"): [
                pathlib.Path(path / "all_types" / "fake.js").resolve(),
            ],
            pathlib.Path("fake.json"): [
                pathlib.Path(path / "all_types" / "fake.json").resolve(),
                pathlib.Path(path / "other_types" / "fake.json").resolve(),
            ],
            pathlib.Path("fake.jsonc"): [
                pathlib.Path(path / "all_types" / "fake.jsonc").resolve(),
            ],
            pathlib.Path("fake.markdown"): [
                pathlib.Path(path / "all_types" / "fake.markdown").resolve(),
            ],
            pathlib.Path("fake.markdownlintignore"): [
                pathlib.Path(
                    path / "all_types" / "fake.markdownlintignore"
                ).resolve(),
            ],
            pathlib.Path("fake.md"): [
                pathlib.Path(path / "all_types" / "fake.md").resolve(),
                pathlib.Path(path / "few_types" / "fake.md").resolve(),
                pathlib.Path(path / "other_types" / "fake.md").resolve(),
            ],
            pathlib.Path("fake.mkdown"): [
                pathlib.Path(path / "all_types" / "fake.mkdown").resolve(),
            ],
            pathlib.Path("fake.nix"): [
                pathlib.Path(path / "all_types" / "fake.nix").resolve(),
            ],
            pathlib.Path("fake.py"): [
                pathlib.Path(path / "all_types" / "fake.py").resolve(),
            ],
            pathlib.Path("fake.sh"): [
                pathlib.Path(path / "all_types" / "fake.sh").resolve(),
            ],
            pathlib.Path("fake.toml"): [
                pathlib.Path(path / "all_types" / "fake.toml").resolve(),
                pathlib.Path(path / "few_types" / "fake.toml").resolve(),
                pathlib.Path(path / "other_types" / "fake.toml").resolve(),
            ],
            pathlib.Path("fake.ts"): [
                pathlib.Path(path / "all_types" / "fake.ts").resolve(),
            ],
            pathlib.Path("fake.txt"): [
                pathlib.Path(path / "all_types" / "fake.txt").resolve(),
            ],
            pathlib.Path("fake.yaml"): [
                pathlib.Path(path / "all_types" / "fake.yaml").resolve(),
                pathlib.Path(path / "other_types" / "fake.yaml").resolve(),
            ],
            pathlib.Path("fake.yml"): [
                pathlib.Path(path / "all_types" / "fake.yml").resolve(),
            ],
            pathlib.Path("fake.zsh"): [
                pathlib.Path(path / "all_types" / "fake.zsh").resolve(),
            ],
            pathlib.Path("fake_empty.json"): [
                pathlib.Path(
                    path / "other_types" / "fake_empty.json"
                ).resolve(),
            ],
            pathlib.Path("fake_list.json"): [
                pathlib.Path(path / "all_types" / "fake_list.json").resolve(),
                pathlib.Path(path / "other_types" / "fake_list.json").resolve(),
            ],
            pathlib.Path("folder_cfg") / "fake.toml": [
                pathlib.Path(
                    path / "few_types" / "folder_cfg" / "fake.toml"
                ).resolve(),
            ],
            pathlib.Path("main/another_fake.md"): [
                pathlib.Path(
                    path / "other_types" / "main" / "another_fake.md"
                ).resolve(),
            ],
            pathlib.Path("main/fake.json"): [
                pathlib.Path(
                    path / "other_types" / "main" / "fake.json"
                ).resolve(),
            ],
            pathlib.Path("main/fake.md"): [
                pathlib.Path(
                    path / "other_types" / "main" / "fake.md"
                ).resolve(),
            ],
            pathlib.Path("main/fake.yaml"): [
                pathlib.Path(
                    path / "other_types" / "main" / "fake.yaml"
                ).resolve(),
            ],
            pathlib.Path("main/fake_merge.yaml"): [
                pathlib.Path(
                    path / "other_types" / "main" / "fake_merge.yaml"
                ).resolve(),
            ],
        }
        config = {
            const.DOTGIT: {
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
            const.DOTGIT: {
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
            const.DOTGIT: {
                const.SOURCE: {
                    const.GIT: {const.URL: repo.working_dir},
                },
            },
        }
        utils.clone_template_repo(config)
        cloned_repo = git.Repo(
            pathlib.Path(config[const.DOTGIT][const.SOURCE][const.PATH])
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
            const.DOTGIT: {
                const.SOURCE: {
                    const.GIT: {const.URL: url, const.REF: ref},
                },
            },
        }
        utils.clone_template_repo(config)
        cloned_repo = git.Repo(
            pathlib.Path(config[const.DOTGIT][const.SOURCE][const.PATH])
        )
        assert (
            str(cloned_repo.head.commit)
            == "2532876902b28883c6b0f736453f61a712f6d97b"
        )
        shutil.rmtree(cloned_repo.working_dir)
