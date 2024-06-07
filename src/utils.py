#!/usr/bin/env python3

import importlib
import inspect
import json
import logging
import os
import tempfile

import git
import yaml

import const

log = logging.getLogger(f"{const.PKG_NAME}")


def get_template_dir(config: dict, tpl_type: str) -> list[str]:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    if "source" in config and tpl_type == "licenses":
        return os.path.join(importlib.resources.files(), "templates", tpl_type)
    return os.path.join(config["source"]["path"], tpl_type)


def template_exists(filename: str, tpl_src: str) -> os.path:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    for inode in os.listdir(tpl_src):
        tplpath = os.path.join(tpl_src, inode)
        if os.path.isfile(tplpath) and str.lower(filename) == str.lower(
            os.path.splitext(inode)[0]
        ):
            return tplpath
    return None


def merge_json_dict(src, update):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    for key, value in update.items():
        if src is None:
            src = {}
        if key not in src:
            src[key] = update[key]
            continue
        if key in src:
            if isinstance(value, dict):
                merge_json_dict(src[key], update[key])
            if isinstance(value, list):
                merge_json_list(src[key], update[key])
            if isinstance(value, (str, int, float)):
                src[key] = update[key]
    return src


def merge_json_list(src: list, update):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    if src and not isinstance(src[0], type(update[0])):
        raise ValueError(f"Different types! {type(src[0])}, {type(update[0])}")

    if not src or len(src) == 0:
        src = update
    else:
        for item in update:
            if item not in src:
                src.append(item)
    return src


def clone_template_repo(config: dict) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    config["source"]["path"] = tempfile.mkdtemp()
    git_url = config["source"]["git"]["url"]

    log.debug("Cloning template source from %s", git_url)
    repo = git.Repo.clone_from(git_url, config["source"]["path"])

    if "ref" in config["source"]["git"]:
        log.debug("Checkout to ref :%s", config["source"]["git"]["ref"])
        repo.git.checkout(config["source"]["git"]["ref"])


def merge_json_content(content, update):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    if isinstance(content, list):
        merge_json_list(content, update)
    elif isinstance(content, dict):
        merge_json_dict(content, update)
    return content


def load_json(src: os.path):
    with open(src, "r", encoding="utf-8") as file:
        content = json.load(file)
    return content


def _concat_file_content(tpl_dir, src, parent, subdir=None):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    if subdir is None:
        subdir = []

    basename = os.path.basename(src)
    with open(src, "r", encoding="utf-8") as tpl_file:
        content = tpl_file.read()

    for curr_dir in subdir:
        file = os.path.join(tpl_dir, curr_dir, parent, basename)
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as tpl_file:
                content += tpl_file.read()
    return content


def _process_dir_template(path: str, parent: str, processed: dict) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    for node in os.listdir(path):
        file_path = os.path.join(path, node)
        key = os.path.join(parent, node)
        if os.path.isfile(file_path):
            if key not in processed:
                processed[key] = []
            processed[key].append(file_path)
        elif os.path.isdir(file_path):
            _process_dir_template(file_path, key, processed)


def compute_template_files(config: dict, tpl_type: str, processed: dict) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    tpl_src = get_template_dir(config, tpl_type)
    if os.path.isdir(tpl_src):
        for curr_dir in config[tpl_type]:
            if not os.path.exists(os.path.join(tpl_src, curr_dir)):
                log.warn("Template directory %s of type %s does not exists in template source", curr_dir, tpl_type)
            else:
                _process_dir_template(os.path.join(tpl_src, curr_dir), "", processed)
