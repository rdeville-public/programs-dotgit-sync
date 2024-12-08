#!/usr/bin/env python3
"""Module testing dogtit.utils.config."""

import inspect
import logging
import pathlib
import shutil

from dotgit_sync import argparser
from dotgit_sync.utils import config as utils, const
import ordered_set
import pytest
import ruamel.yaml


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestUtilsMigrateConfig:
    """Collection to test utility config."""

    _script_path = pathlib.Path(__file__).parent
    _script_name = pathlib.Path(__file__).stem
    _output_dir = _script_path.parent / "fake_repo"
    _config_dir = _script_path.parent / "fake_config"
    _config_file = _config_dir / "valid.with_source_path.dotgit.yaml"
    _from = const.CFG_VERSIONS[-1]
    _to = "vFake"
    _args = None

    @pytest.fixture(autouse=True)
    def _inject_fixtures(self, caplog: str) -> None:
        self._caplog = caplog

    def test_missing_migration(self) -> None:
        """Ensure an error is thrown if a migration is missing."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw a `FileNotFoundError`")

        const.CFG_VERSIONS.append(self._to)
        self._args = argparser.parser().parse_args([
            "-c",
            str(self._config_file),
        ])
        with pytest.raises(FileNotFoundError) as error:
            utils.migrate_config.check_migrations(self._args)
        error_msg = f"Missing migration {self._from}_{self._to}.py"
        const.CFG_VERSIONS.pop()
        assert error.type is FileNotFoundError
        assert error.match(error_msg)

    def test_useless_migrations(self) -> None:
        """Ensure a warning is printing if a migration seems useless."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should log a warning if a migration seems useless")

        useless_migration = (
            self._script_path.parent.parent
            / const.PKG_NAME
            / const.MIGRATIONS
            / f"{const.CFG_VERSIONS[0]}_{self._to}.py"
        )
        with useless_migration.open("w") as stream:
            stream.write("")

        migration_name = f"{const.CFG_VERSIONS[0]}_{self._to}"
        self._args = argparser.parser().parse_args([
            "-c",
            str(self._config_file),
        ])
        utils.migrate_config.check_migrations(self._args)
        useless_migration.unlink()
        warning_msg = f"Migration {migration_name} does not seem to be used"
        assert warning_msg in self._caplog.text

    def test_first_migration_warning(self) -> None:
        """Ensure a warning is printing for initial migration."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should log a warning for initial v0 migration")

        old_cfg_version = const.CFG_VERSIONS
        const.CFG_VERSIONS = ordered_set.OrderedSet([const.CFG_VERSIONS[0]])
        cfg_path = (
            self._script_path.parent
            / f"{const.MIGRATIONS}_test"
            / f"{const.CFG_VERSIONS[0]}_test"
            / "from.yaml"
        )

        self._args = argparser.parser().parse_args([
            "-c",
            str(cfg_path),
        ])
        required, config = utils.migrate_config.check_migrations(self._args)
        const.CFG_VERSIONS = old_cfg_version
        warning_msg = f"Your config file `{cfg_path}` does not have required key `version`"  # noqa: E501
        assert warning_msg in self._caplog.text
        assert not required
        assert config[const.VERSION] == const.CFG_VERSIONS[0]

    def test_first_migration(self) -> None:
        """Ensure a warning is printing for initial migration."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should dynamically add key `version: v0` to config")

        old_cfg_version = const.CFG_VERSIONS
        const.CFG_VERSIONS = ordered_set.OrderedSet([const.CFG_VERSIONS[0]])
        cfg_path = (
            self._script_path.parent
            / f"{const.MIGRATIONS}_test"
            / f"{const.CFG_VERSIONS[0]}_test"
            / "from.yaml"
        )

        self._args = argparser.parser().parse_args([
            "-c",
            str(cfg_path),
            "--migrate",
        ])
        required, config = utils.migrate_config.check_migrations(self._args)
        const.CFG_VERSIONS = old_cfg_version
        assert not required
        assert config[const.VERSION] == const.CFG_VERSIONS[0]

    def test_process_all_migrations_from_initial(self) -> None:
        """Ensure migrations are working since initial config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should dynamically add key `version: v0` to config")

        cfg_to = (
            self._script_path
            / self._script_name
            / f"{const.CFG_VERSIONS[-1]}.yaml"
        )
        shutil.copy(
            self._script_path / self._script_name / "initial.yaml",
            self._output_dir / ".dotgit.yaml",
        )
        self._args = argparser.parser().parse_args([
            "-c",
            str(self._output_dir / ".dotgit.yaml"),
            "-o",
            str(self._output_dir),
            "--migrate",
        ])
        config = utils.migrate_config.process_migration(self._args)

        self._args = argparser.parser().parse_args([
            "-c",
            str(cfg_to),
        ])

        yaml = ruamel.yaml.YAML()
        with self._args.config.open(encoding="utf-8") as stream:
            migrated_config = yaml.load(stream)

        assert config == migrated_config

    def test_process_all_possible_migrations(self) -> None:
        """Ensure migrations are working from any versions."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should dynamically add key `version: v0` to config")

        for idx in range(len(const.CFG_VERSIONS) - 1):
            cfg_to = (
                self._script_path
                / self._script_name
                / f"{const.CFG_VERSIONS[-1]}.yaml"
            )
            shutil.copy(
                self._script_path
                / self._script_name
                / f"{const.CFG_VERSIONS[idx]}.yaml",
                self._output_dir / ".dotgit.yaml",
            )
            self._args = argparser.parser().parse_args([
                "-c",
                str(self._output_dir / ".dotgit.yaml"),
                "-o",
                str(self._output_dir),
                "--migrate",
            ])
            config = utils.migrate_config.process_migration(self._args)

            self._args = argparser.parser().parse_args([
                "-c",
                str(cfg_to),
            ])

            yaml = ruamel.yaml.YAML()
            with self._args.config.open(encoding="utf-8") as stream:
                migrated_config = yaml.load(stream)

            assert config == migrated_config
