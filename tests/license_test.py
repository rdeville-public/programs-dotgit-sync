#!/usr/bin/env python3
"""Module testing dotgit_sync.license."""

import copy
import inspect
import logging
import pathlib
import shutil

from dotgit_sync import licenses
from dotgit_sync.utils import const, templates as utils
import pytest


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestLicenses:
    """Collection suite to test license."""

    _script_path = pathlib.Path(__file__).parent
    _tpl_source = _script_path / "fake_licenses"
    _output_dir = _script_path / "fake_repo"
    _out_primary = _output_dir / "LICENSE"
    _out_secondary = _output_dir / "LICENSE.BEERWARE"
    _out_copyright = _output_dir / "COPYRIGHT"
    _target_primary = _tpl_source / "render.LICENSE.MIT"
    _target_secondary = _tpl_source / "render.LICENSE.BEERWARE"
    _target_copyright = _tpl_source / "render.COPYRIGHT"
    _config = {  # noqa: RUF012
        const.OUTDIR: _output_dir,
        "name": "program",
        "description": "Program Description",
        const.PKG_NAME: {
            const.SOURCE: {const.PATH: _tpl_source},
        },
        const.LICENSES: {
            const.DATE: {
                const.FIRST_YEAR: 1970,
                const.CURR_YEAR: 2100,
            },
            const.COPYRIGHT: {
                "owner": "Full Name",
                "email": "mail@domain.tld",
            },
            const.PRIMARY: "MIT",
            const.SECONDARIES: [
                "BEERWARE",
            ],
        },
    }

    @pytest.fixture(autouse=True)
    def _remove_rendered_files(self) -> None:
        for node in self._output_dir.iterdir():
            node_path = pathlib.Path(self._output_dir) / node
            if node_path.is_dir():
                shutil.rmtree(node_path)
            elif node_path.is_file() and node_path.name != ".gitkeep":
                node_path.unlink()

    @pytest.fixture(autouse=True)
    def _inject_fixtures(self, caplog: str) -> None:
        self._caplog = caplog

    def test_unsupported_license_name(self) -> None:
        """Test license name not supported."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as license template does not exists")

        config = {
            const.PKG_NAME: {const.SOURCE: {const.PATH: {self._tpl_source}}}
        }
        tpl_src = utils.get_template_dir(config, const.LICENSES)
        with pytest.raises(FileNotFoundError) as error:
            licenses._render_license(config, tpl_src, "foo")  # noqa : SLF0001
        assert "There are not template license foo" in str(error.value)

    def test_rendering_single_primary_license(self) -> None:
        """Test when only single primary license if provided."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT license in fake repo")

        config = copy.deepcopy(self._config)
        tpl_src = utils.get_template_dir(config, const.LICENSES)
        licenses._render_license(config, tpl_src, "MIT", True)  # noqa : SLF0001
        assert self._out_primary.read_text(
            encoding="utf-8"
        ) == self._target_primary.read_text(encoding="utf-8")

    def test_rendering_single_secondary_license(self) -> None:
        """Test when single primary and single secondary licenses if provided."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write BEERWARE license in fake repo")

        config = copy.deepcopy(self._config)
        tpl_src = utils.get_template_dir(config, const.LICENSES)
        licenses._render_license(config, tpl_src, "BEERWARE")  # noqa : SLF0001
        assert self._out_secondary.read_text(
            encoding="utf-8"
        ) == self._target_secondary.read_text(encoding="utf-8")

    def test_rendering_from_config_single_primary(self) -> None:
        """Test rendering license when in config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT and BEERWARE licenses in fake repo")

        config = copy.deepcopy(self._config)
        config[const.LICENSES].pop(const.SECONDARIES)
        licenses.process(config)
        assert self._out_primary.read_text(
            encoding="utf-8"
        ) == self._target_primary.read_text(encoding="utf-8")

    def test_rendering_from_config_primary_and_secondary(self) -> None:
        """Test rendering primary and secondary licenses."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT and BEERWARE licenses in fake repo")

        config = copy.deepcopy(self._config)
        licenses.process(config)
        assert self._out_secondary.read_text(
            encoding="utf-8"
        ) == self._target_secondary.read_text(encoding="utf-8")
        assert self._out_primary.read_text(
            encoding="utf-8"
        ) == self._target_primary.read_text(encoding="utf-8")

    def test_rendering_from_config_primary_and_wrong_secondary(self) -> None:
        """Test rendering primary and wrong secondary licenses."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT licenses in fake repo and print a warning")

        config = copy.deepcopy(self._config)
        config[const.LICENSES][const.SECONDARIES] = ["foo"]
        licenses.process(config)
        assert self._out_primary.read_text(
            encoding="utf-8"
        ) == self._target_primary.read_text(encoding="utf-8")
        assert "There are not template license foo" in self._caplog.text

    def test_rendering_from_config_primary_and_empty_secondary(self) -> None:
        """Test primary license and empty secondary license."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT licenses in fake repo")

        config = copy.deepcopy(self._config)
        config[const.LICENSES][const.SECONDARIES] = []
        licenses.process(config)
        assert self._out_primary.read_text(
            encoding="utf-8"
        ) == self._target_primary.read_text(encoding="utf-8")

    def test_rendering_from_config_with_wrong_license(self) -> None:
        """Test rendering when unsupported license is provided."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return None as licenses does not exists")

        config = {
            const.PKG_NAME: {
                const.SOURCE: {const.PATH: self._tpl_source},
            },
            const.LICENSES: {
                const.PRIMARY: "foo",
            },
        }
        ret = licenses.process(config)
        assert "There are not template license foo" in self._caplog.text
        assert ret is None

    def test_rendering_from_config_copyright(self) -> None:
        """Test rendering license when in config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT and BEERWARE licenses in fake repo")

        config = copy.deepcopy(self._config)
        config[const.LICENSES].pop(const.SECONDARIES)
        config[const.LICENSES][const.PRIMARY] = "COPYRIGHT"
        licenses.process(config)
        assert self._out_copyright.read_text(
            encoding="utf-8"
        ) == self._target_copyright.read_text(encoding="utf-8")

    def test_rendering_from_config_copyright_and_secondary(self) -> None:
        """Test rendering license when in config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write MIT and BEERWARE licenses in fake repo")

        config = copy.deepcopy(self._config)
        config[const.LICENSES][const.PRIMARY] = "COPYRIGHT"
        with pytest.raises(ValueError) as error:
            licenses.process(config)
        err_msg = f"There can't be a licenses {licenses._COPYRIGHT} and a secondary license"  # noqa: SLF001, E501
        assert err_msg in str(error.value)
