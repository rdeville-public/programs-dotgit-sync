#!/usr/bin/env python3

import inspect
import logging
import os
import pathlib
import shutil

from dotgit_sync import main


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestMain:
    _script_path = pathlib.Path(__file__).parent
    _output_dir = _script_path / "fake_repo"
    _config_dir = _script_path / "fake_config"
    _tpl_dir = _script_path / "fake_templates"

    #  @pytest.fixture(autouse=True)
    #  def _remove_rendered_files(self):
    #      for node in os.listdir(self._output_dir):
    #          node_path = pathlib.Path(self._output_dir) / node
    #          if node_path.is_dir():
    #              shutil.rmtree(node_path)
    #          elif node_path.is_file() and node_path.name != ".gitkeep":
    #              node_path.unlink()
    def _assert_rendering(
        self, render_dir: pathlib.Path, output_dir: pathlib.Path
    ) -> None:
        for file in os.listdir(render_dir):
            assert (render_dir / file).read_text() == (
                output_dir / file
            ).read_text()

    def test_main(self) -> None:
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
