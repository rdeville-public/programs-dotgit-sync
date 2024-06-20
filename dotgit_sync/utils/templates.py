#!/usr/bin/env python3
"""Set of utility method to manipulate or process template."""

import inspect
import logging
import os
import pathlib
import tempfile

import git

from . import const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def clone_template_repo(config: dict) -> None:
    """Clone git repository storing templates.

    Args:
        config: Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config[const.PKG_NAME][const.SOURCE][const.PATH] = tempfile.mkdtemp()
    git_url = config[const.PKG_NAME][const.SOURCE][const.GIT][const.URL]

    log.debug("Cloning template source from %s", git_url)
    repo = git.Repo.clone_from(
        git_url, config[const.PKG_NAME][const.SOURCE][const.PATH]
    )

    if "ref" in config[const.PKG_NAME][const.SOURCE][const.GIT]:
        log.debug(
            "Checkout to ref :%s",
            config[const.PKG_NAME][const.SOURCE][const.GIT][const.REF],
        )
        repo.git.checkout(
            config[const.PKG_NAME][const.SOURCE][const.GIT][const.REF]
        )


def get_template_dir(config: dict, tpl_type: str) -> pathlib.Path:
    """Get folders storing templates from configuration.

    Args:
        config: Dotgit Sync configuration
        tpl_type: Type of template folder to look for, templates or statics

    Return:
        Path to folder storing templates
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if tpl_type == const.LICENSES:
        return pathlib.Path(__file__).parent.parent / const.TEMPLATES / tpl_type
    return (
        pathlib.Path(config[const.PKG_NAME][const.SOURCE][const.PATH])
        / tpl_type
    )


def template_exists(filename: str, tpl_src: str) -> pathlib.Path | None:
    """Check if a specific file exists in template subfolder.

    Args:
        filename: Name of the file to search for
        tpl_src: Path to the subfolder storing templates

    Return:
        The path to the file in the subfolder or None
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    for inode in os.listdir(tpl_src):
        tplpath = pathlib.Path(tpl_src) / inode
        if tplpath.is_file() and str.lower(filename) == str.lower(
            pathlib.Path(inode).name
        ):
            return tplpath
    return None


def _process_dir_template(path: str, parent: str, processed: dict) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    for node in os.listdir(path):
        file_path = pathlib.Path(path) / node
        key = pathlib.Path(parent) / node
        if pathlib.Path(file_path).is_file():
            if key not in processed:
                processed[key] = []
            processed[key].append(file_path)
        else:  # pathlib.Path(file_path).is_dir():
            _process_dir_template(file_path, key, processed)


def compute_template_files(
    config: dict, tpl_type: str, processed: dict
) -> None:
    """Entrypoint method to render destination file.

    Args:
        config: Dotgit Sync configuration
        tpl_type: Type of template to process, either templates or statics
        processed: Dictionnary storing templates information
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    tpl_src = get_template_dir(config, tpl_type)
    for curr_dir in config[tpl_type]:
        if not pathlib.Path(pathlib.Path(tpl_src) / curr_dir).exists():
            log.warning(
                "Directory '%s' of type '%s' is not in template source",
                curr_dir,
                tpl_type,
            )
        else:
            _process_dir_template(
                pathlib.Path(tpl_src) / curr_dir, "", processed
            )
