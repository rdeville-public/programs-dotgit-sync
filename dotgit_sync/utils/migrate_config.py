#!/usr/bin/env python3
"""Set of utility method to process migration of config file."""

import argparse
import inspect
import logging
import pathlib
import re

from ruamel.yaml import ruamel
import yaml

from .. import migrations
from . import config as cfg_utils, const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / const.MIGRATIONS


def _print_v0_warning(config_file_path: str) -> None:
    log.warning(
        "Your config file `%s` does not have required key `version`",
        config_file_path,
    )
    log.warning(
        "Program assume it's an old config file structure, will be set to %s",
        const.CFG_VERSIONS[0],
    )
    log.warning("You should update your config file, to do so, you can :")
    log.warning(" * Add the key `version` to your config file")
    log.warning(
        " * Use `--migrate` to update your config file to latest version."
    )


def _list_migrations() -> list[pathlib.Path]:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    migrations: list[pathlib.Path] = [
        inode
        for inode in _MIGRATIONS_DIR.iterdir()
        if pathlib.Path.is_file(_MIGRATIONS_DIR / inode)
        and inode.name != "__init__.py"
        and re.match(r".*.py", inode.name)
    ]

    migrations.sort(key=lambda file: (_MIGRATIONS_DIR / file).stat().st_mtime)

    return migrations


def _check_missing_migrations() -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    migrations = _list_migrations()
    migrations.pop(0)
    migration_names = [migration.stem for migration in migrations]

    nb_versions = len(const.CFG_VERSIONS)

    for idx_version in range(nb_versions - 1):
        from_version = const.CFG_VERSIONS[idx_version]
        to_version = const.CFG_VERSIONS[idx_version + 1]
        migration_name = f"{from_version}_{to_version}"

        if migration_name not in migration_names:
            msg = f"Missing migration {from_version}_{to_version}.py"
            raise FileNotFoundError(msg)

        migration_names.pop(migration_names.index(migration_name))

    if len(migration_names) != 0:
        [
            log.warning("Migration %s does not seem to be used", migration_name)
            for migration_name in migration_names
        ]


def check_migrations(args: argparse.Namespace) -> tuple[bool, dict]:
    """Check migrations to apply.

    Check if there is no missing migrations and if there is migrations to apply
    to update configuration file struture.

    Args:
        args: Arguments passed to programs

    Returns:
        bool: True if there is migrations to apply, False otherwise
        dict: The content of the configuration from the dotgit config file
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    last_version = const.CFG_VERSIONS[-1]

    _check_missing_migrations()

    with args.config.open() as stream:
        config = yaml.safe_load(stream)

    git_root_dir = cfg_utils.search_git_workdir(pathlib.Path.cwd())
    config_file_path = str(args.config).replace(f"{git_root_dir!s}/", "")

    if const.VERSION not in config:
        if not args.migrate:
            _print_v0_warning(config_file_path)
        config[const.VERSION] = const.CFG_VERSIONS[0]

    cfg_file_version = config[const.VERSION]

    if last_version == cfg_file_version:
        log.info("Config file seems up to date")
        return False, config

    return True, config


def _compute_migrations_to_process(config: dict) -> list[str]:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    migrations = [migration.stem for migration in _list_migrations()]

    if const.VERSION not in config:
        return migrations

    version_idx = migrations.index(config[const.VERSION])
    migrations_to_apply = []

    for idx in range(version_idx, len(const.CFG_VERSIONS) - 1):
        from_version = const.CFG_VERSIONS[idx]
        to_version = const.CFG_VERSIONS[idx + 1]
        migrations_to_apply.append(f"{from_version}_{to_version}")

    return migrations_to_apply


def process_migration(args: argparse.Namespace) -> dict:
    """Apply migrations to upgrade config and write new config structure.

    Args:
        args: Arguments passed to programs

    Returns:
        dict: The content of the configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Running migrations")

    yaml = ruamel.yaml.YAML()
    with args.config.open(encoding="utf-8") as stream:
        config = yaml.load(stream)

    migrations_list = _compute_migrations_to_process(config)

    for migration in migrations_list:
        getattr(migrations, f"{migration}").up(config)

    with args.config.open("w", encoding="utf-8") as stream:
        yaml.indent(mapping=2, sequence=0, offset=2)
        yaml.dump(config, stream)

    return config
