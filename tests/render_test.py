#!/usr/bin/env python3
"""Module testing dotgit_sync.render."""

import inspect
import logging
import pathlib
import shutil

from dotgit_sync import render
from dotgit_sync.utils import const
import json5
import pytest
import yaml


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestRender:
    """Collection testing rendering methods."""

    _script_path = pathlib.Path(__file__).parent
    _tpl_dir = _script_path / "fake_templates"
    _target_out_dir = _script_path / "fake_rendered"
    _output_dir = _script_path / "fake_repo"
    _fake_md_tpl_file = (
        _script_path
        / "fake_templates"
        / "templates"
        / "other_types"
        / "fake.md"
    )

    @pytest.fixture(autouse=True)
    def _prepare_fake_repo(self) -> None:
        for node in self._output_dir.iterdir():
            node_path = self._output_dir / node
            if node_path.is_dir():
                shutil.rmtree(node_path)
            elif node_path.is_file() and node_path.name != ".gitkeep":
                node_path.unlink()

    @staticmethod
    def _test_marks(ft: str, target: dict) -> None:
        marks = render._get_mark_comment(ft)  # noqa: SLF001
        assert marks == target

    @staticmethod
    def _test_merge_contexts(
        rendered_file: pathlib.Path,
        tpl_file: pathlib.Path,
        target: dict,
        marks: dict,
    ) -> None:
        contexts = render._merge_contexts(  # noqa: SLF001
            render._extract_context_from_rendered_file(  # noqa: SLF001
                rendered_file, marks
            ),
            render._extract_context_from_template(  # noqa: SLF001
                str(tpl_file.read_text()), marks
            ),
        )
        assert contexts == target

    def _test_rendering_file(
        self, dest: pathlib.Path, target: pathlib.Path, is_static: bool = False
    ) -> None:
        config = {
            const.OUTDIR: self._output_dir,
            "description": "Program Description",
        }
        render.render_file(
            config,
            dest,
            self._fake_md_tpl_file.read_text(),
            const.MD,
            is_static=is_static,
        )
        assert dest.read_text() == target.read_text()

    def _test_rendering_json_yaml(
        self,
        dest: pathlib.Path,
        update_file: pathlib.Path,
        target_file: pathlib.Path,
        ft: str,
    ) -> None:
        config = {
            const.OUTDIR: self._output_dir,
            "description": "Program Description",
        }
        if ft == const.YAML:
            update = yaml.safe_load(update_file.read_text())
            target = yaml.safe_load(target_file.read_text())
        else:
            update = json5.loads(update_file.read_text())
            target = json5.loads(target_file.read_text())
        render.render_json(config, dest, update, ft, enforce=False)
        if ft == const.YAML:
            content = yaml.safe_load(dest.read_text())
        else:
            content = json5.loads(dest.read_text())
        assert content == target

    def test_extract_context_from_template(self) -> None:
        """Test dictionnary with context are correctly built from template."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return a dictionnary with template content")

        marks = render._get_mark_comment(const.MD)  # noqa: SLF001
        context = render._extract_context_from_template(  # noqa: SLF001
            str(self._fake_md_tpl_file.read_text()), marks
        )
        target_context = {
            "templatebefore": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "# Markdwon Title\n\nRender from jinja below :\n{{ description }}\n\n",  # noqa: E501, SLF001
            },
            "TAG_EXCLUDE": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "Content Excluded from template\n\nCustomized by user\n\n",  # noqa: E501, SLF001
            },
            "templateTAG_EXCLUDE": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "\n## Markdwon Subtitle\n\nWith some content\n",  # noqa: SLF001, E501
            },
        }
        assert context == target_context

    def test_extract_context_from_rendered_files(self) -> None:
        """Test dictionnary with context are correctly built from rendered file."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Return a dictionnary with rendered file content")

        fake_rendered_file = (
            self._script_path / "fake_rendered" / "fake_templates.md"
        )
        marks = render._get_mark_comment(const.MD)  # noqa: SLF001
        context = render._extract_context_from_rendered_file(  # noqa: SLF001
            fake_rendered_file, marks
        )
        target_context = {
            "before": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "Context Before\n",  # noqa: SLF001
            },
            "templatebefore": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "# Markdwon Title\n\nRender from jinja below :\nProgram Description\n\n",  # noqa: E501, SLF001
            },
            "TAG_EXCLUDE": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "Content Excluded from template\n\nCustomized by user\n\n",  # noqa: E501, SLF001
            },
            "templateTAG_EXCLUDE": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "\n## Markdwon Subtitle\n\nWith some content\n",  # noqa: E501, SLF001
            },
            "after": {
                render._INDENT: "",  # noqa: SLF001
                render._CONTENT: "Context After\n",  # noqa: SLF001
            },
        }
        assert context == target_context

    def test_merge_contexts(self) -> None:
        """Test merging dictionnary with contexts is done correctly."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Return a dictionnary with file content to write handling customize excluded content"  # noqa: E501
        )

        rendered_file = self._script_path / "fake_rendered" / "fake_statics.md"
        marks = render._get_mark_comment(const.MD)  # noqa: SLF001
        self._test_merge_contexts(
            rendered_file,
            self._fake_md_tpl_file,
            {
                "before": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Context Before\n",  # noqa: SLF001
                },
                "templatebefore": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "# Markdwon Title\n\nRender from jinja below :\n{{ description }}\n\n",  # noqa: E501, SLF001
                },
                "TAG_EXCLUDE": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Content Excluded from template\n\nCustomized by user\n\n",  # noqa: E501, SLF001
                },
                "templateTAG_EXCLUDE": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "\n## Markdwon Subtitle\n\nWith some content\n",  # noqa: E501, SLF001
                },
                "after": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Context After\n",  # noqa: SLF001
                },
            },
            marks,
        )
        self._test_merge_contexts(
            rendered_file,
            self._script_path
            / "fake_templates"
            / const.TEMPLATES
            / "other_types"
            / "fake.md",
            {
                "before": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Context Before\n",  # noqa: SLF001
                },
                "templatebefore": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "# Markdwon Title\n\nRender from jinja below :\n{{ description }}\n\n",  # noqa: E501, SLF001
                },
                "TAG_EXCLUDE": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Content Excluded from template\n\nCustomized by user\n\n",  # noqa: E501, SLF001
                },
                "templateTAG_EXCLUDE": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "\n## Markdwon Subtitle\n\nWith some content\n",  # noqa: E501, SLF001
                },
                "after": {
                    render._INDENT: "",  # noqa: SLF001
                    render._CONTENT: "Context After\n",  # noqa: SLF001
                },
            },
            marks,
        )

    def test_create_dest_dir(self) -> None:
        """Test creation of destination directory."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Create parent directory tree of dest file if not exists")

        fake_dest_file = (
            self._script_path / "fake_repo" / "foo" / "bar" / "baz.md"
        )
        render._create_dest_dir(fake_dest_file)  # noqa: SLF001
        assert fake_dest_file.parent.exists()
        assert fake_dest_file.parent.is_dir()

    def test_build_of_marks_comment(self) -> None:
        """Test the build of marks used for block comment."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return right comment marks for specified ft")
        self._test_marks(const.MD, {const.BEGIN: "<!--", const.END: " -->"})
        self._test_marks(const.SH, {const.BEGIN: "#", const.END: ""})
        self._test_marks(const.JS, {const.BEGIN: "/*", const.END: " */"})
        self._test_marks(const.J2, {const.BEGIN: "{#-", const.END: " -#}"})
        self._test_marks("no_comment_for_filetype", {})

    def test_rendering_file(self) -> None:
        """Test rendering a fingle file."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return right comment marks for specified ft")
        dest = self._output_dir / "fake.md"
        target = (
            self._script_path
            / "fake_rendered"
            / "fake_templates_no_outside_context.md"
        )
        self._test_rendering_file(dest, target)

        # Fake adding before and after context and update excluded context
        target = self._script_path / "fake_rendered" / "fake_templates.md"
        shutil.copy(target, dest)
        self._test_rendering_file(dest, target)

        target = self._script_path / "fake_rendered" / "fake_statics.md"
        self._test_rendering_file(dest, target, True)

    def test_rendering_json_yaml(self) -> None:
        """Test rendering a json and yaml file."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return right comment marks for specified ft")
        dest = self._output_dir / "fake.json"
        update = (
            self._script_path
            / "fake_templates"
            / const.TEMPLATES
            / "other_types"
            / "fake.json"
        )
        target = (
            self._script_path / "fake_rendered" / "fake_json_no_custom_key.json"
        )
        self._test_rendering_json_yaml(dest, update, target, const.JSON)
        target = (
            self._script_path
            / "fake_rendered"
            / "fake_json_with_custom_key.json"
        )
        shutil.copy(target, dest)
        self._test_rendering_json_yaml(dest, update, target, const.JSON)
        dest.unlink()
        update = (
            self._script_path
            / "fake_templates"
            / const.TEMPLATES
            / "other_types"
            / "fake_list.json"
        )
        target = (
            self._script_path
            / "fake_rendered"
            / "fake_list_json_no_custom_key.json"
        )
        self._test_rendering_json_yaml(dest, update, target, const.JSON)

        dest = self._output_dir / "fake.yaml"
        update = (
            self._script_path
            / "fake_templates"
            / const.TEMPLATES
            / "other_types"
            / "fake.yaml"
        )
        target = (
            self._script_path / "fake_rendered" / "fake_yaml_no_custom_key.yaml"
        )
        self._test_rendering_json_yaml(dest, update, target, const.YAML)
        target = (
            self._script_path
            / "fake_rendered"
            / "fake_yaml_with_custom_key.yaml"
        )
        shutil.copy(target, dest)
        self._test_rendering_json_yaml(dest, update, target, const.YAML)
