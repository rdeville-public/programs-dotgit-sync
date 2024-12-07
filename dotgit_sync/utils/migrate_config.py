#!/usr/bin/env python3
"""Set of utility method to process migration of config file"""

import inspect
import logging
import pathlib
import re
import argparse
from typing import Tuple

from ruamel.yaml import ruamel
import yaml

from .. import migrations
from . import const, config as cfg_utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / const.MIGRATIONS


def _print_v0_warning(config_file_path: str) -> None:
    log.warning(
        f"Your config file `{config_file_path}` does not have required key `version`"
    )
    log.warning(
        f"Program will assume you use a old config file structure and will be set to {const.CFG_VERSIONS[0]}"
    )
    log.warning(
        "You should update your config file, to do so, you can :"
    )
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
            raise FileNotFoundError(
                f"Missing migration {from_version}_{to_version}.py"
            )

        migration_names.pop(migration_names.index(migration_name))

    if len(migration_names) != 0:
        [
            log.warning(f"Migration {migration_name} does not seem to be used")
            for migration_name in migration_names
        ]


def check_migrations(args: argparse.Namespace) -> Tuple[bool, dict]:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    last_version = const.CFG_VERSIONS[-1]

    _check_missing_migrations()

    with args.config.open() as stream:
        config = yaml.safe_load(stream)

    git_root_dir = cfg_utils.search_git_workdir(pathlib.Path.cwd())
    config_file_path = str(args.config).replace(f"{str(git_root_dir)}/", "")

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


def process_migration(args: argparse.Namespace, config: dict) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Running migrations")

    yaml = ruamel.yaml.YAML()
    with open(args.config) as stream:
        config = yaml.load(stream)

    migrations_list = _compute_migrations_to_process(config)

    for migration in migrations_list:
        getattr(migrations, f"{migration}").up(config)

    with open(args.config, "w") as stream:
        yaml.indent(mapping=2, sequence=0, offset=2)
        yaml.dump(config, stream)

    return config
