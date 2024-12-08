#!/usr/bin/env python3
"""Module testing dotgit_sync.migrations.v0."""

import inspect
import logging
import pathlib

from dotgit_sync import migrations
import ruamel.yaml


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"
_FROM = "from.yaml"
_TO = "to.yaml"


class TestMigrationV0:
    """Collection suite testing migrations.v0."""

    _script_file_path = pathlib.Path(__file__)
    _script_path = _script_file_path.parent
    _from_cfg = _script_path / _script_file_path.stem / _FROM
    _to_cfg = _script_path / _script_file_path.stem / _TO
    _args = None

    def test_v0_up(self) -> None:
        """Test migrations to v0."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should update the configuration to version v0")

        yaml = ruamel.yaml.YAML()
        with self._from_cfg.open(encoding="utf-8") as stream:
            from_cfg = yaml.load(stream)
        with self._to_cfg.open(encoding="utf-8") as stream:
            to_cfg = yaml.load(stream)

        migrations.v0.up(from_cfg)

        assert from_cfg == to_cfg
