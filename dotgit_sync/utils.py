#!/usr/bin/env python3
"""Set of utility method to manipulate template data."""

import importlib
import inspect
import json
import logging
import os
import pathlib
import tempfile

import git

from . import const


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


def get_template_dir(config: dict, tpl_type: str) -> pathlib.Path:
    """Get folders storing templates from configuration.

    Args:
        config: Dotgit Sync configuration
        tpl_type: Type of template folder to look for, templates or statics

    Return:
        Path to folder storing templates
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if "source" in config and tpl_type == "licenses":
        return (
            pathlib.Path(importlib.resources.files()) / "templates" / tpl_type
        )
    return pathlib.Path(config["source"]["path"]) / tpl_type


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


def merge_json_dict(src: dict, update: dict) -> dict:
    """Deeply merge json dictionary.

    Args:
        src: Initial dictionary
        update: New dictionary that will be merge into the initial dictionary

    Return:
        The merged dictionary
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    for key, value in update.items():
        if src is None:
            src = {}
        if key not in src:
            src[key] = value
            continue
        if key in src:
            if isinstance(value, dict):
                merge_json_dict(src[key], value)
            if isinstance(value, list):
                merge_json_list(src[key], value)
            if isinstance(value, (str, int, float)):
                src[key] = value
    return src


def merge_json_list(src: list, update: list) -> list:
    """Deeply merge json list or concat if item does not exists.

    Args:
        src: Initial list
        update: New list that will be concat into the initial dictionary

    Return:
        The merged list
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if src and not isinstance(src[0], type(update[0])):
        error_msg = f"Different types! {type(src[0])}, {type(update[0])}"
        raise ValueError(error_msg)

    if not src or len(src) == 0:
        src = update
    else:
        for item in update:
            if item not in src:
                src.append(item)
    return src


def clone_template_repo(config: dict) -> None:
    """Clone git repository storing templates.

    Args:
        config: Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    config["source"]["path"] = tempfile.mkdtemp()
    git_url = config["source"]["git"]["url"]

    log.debug("Cloning template source from %s", git_url)
    repo = git.Repo.clone_from(git_url, config["source"]["path"])

    if "ref" in config["source"]["git"]:
        log.debug("Checkout to ref :%s", config["source"]["git"]["ref"])
        repo.git.checkout(config["source"]["git"]["ref"])


def merge_json_content(
    content: dict | list, update: dict | list
) -> dict | list:
    """Main method able to merge dict or list.

    Args:
        content: Initial content
        update: Update content that will be merge into the initial one

    Return:
        The same type of the content merge with the update
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if isinstance(content, list):
        merge_json_list(content, update)
    elif isinstance(content, dict):
        merge_json_dict(content, update)
    return content


def load_json(src: pathlib.Path) -> dict | list:
    """Load json content of a file.

    Args:
        src: Path to the json file to load

    Return:
        Either a dict or list depending on the content of the file
    """
    with pathlib.Path(src).open(encoding="utf-8") as file:
        return json.load(file)


def _process_dir_template(path: str, parent: str, processed: dict) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    for node in os.listdir(path):
        file_path = pathlib.Path(path) / node
        key = pathlib.Path(parent) / node
        if pathlib.Path(file_path).is_file():
            if key not in processed:
                processed[key] = []
            processed[key].append(file_path)
        elif pathlib.Path(file_path).is_dir():
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
    if pathlib.Path(tpl_src).is_dir():
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
