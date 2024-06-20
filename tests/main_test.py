#!/usr/bin/env python3
"""Module testing dotgit.main."""

import inspect
import logging
import os
import pathlib
import shutil

from dotgit_sync import main


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestMain:
    """Collection testing main entrypoint of program."""

    _script_path = pathlib.Path(__file__).parent
    _output_dir = _script_path / "fake_repo"
    _config_dir = _script_path / "fake_config"
    _tpl_dir = _script_path / "fake_templates"

    @staticmethod
    def _assert_rendering(
        render_dir: pathlib.Path, output_dir: pathlib.Path
    ) -> None:
        for file in os.listdir(render_dir):
            assert (render_dir / file).read_text() == (
                output_dir / file
            ).read_text()

    def test_main(self) -> None:
        """Test calling main entrypoint of program and ensure rendering."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should accept format 'string', 'String' and 'STRING'")

        render_dir = self._script_path / "fake_rendered" / "main"
        shutil.copy(
            self._config_dir / "main.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        main.main([
            "-c",
            str(self._output_dir / ".dotgit.yaml"),
            "-o",
            str(self._output_dir),
            "-d",
            str(self._tpl_dir),
        ])
        self._assert_rendering(render_dir, self._output_dir)

    def test_main_merge_yaml(self) -> None:
        """Test calling main entrypoint with merge of program and ensure rendering."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should accept format 'string', 'String' and 'STRING'")

        render_dir = self._script_path / "fake_rendered" / "main_merge_yaml"
        shutil.copy(
            self._config_dir / "main.merge_yaml.dotgit.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        main.main([
            "-c",
            str(self._output_dir / ".dotgit.yaml"),
            "-o",
            str(self._output_dir),
            "-d",
            str(self._tpl_dir),
        ])
        self._assert_rendering(render_dir, self._output_dir)
