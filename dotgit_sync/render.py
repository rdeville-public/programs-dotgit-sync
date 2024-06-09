#!/usr/bin/env python3
"""Module which process rendering of output files."""

import inspect
import logging
import os
import pathlib
import re

import jinja2
import json5
import yaml

from . import const, utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_FULL_FILE_TYPE = ["plain", "unknown"]
_BEFORE = "before"
_AFTER = "after"
_TEMPLATE = "template"
_MARK = "DOTGIT-SYNC BLOCK"
_BEGIN_MANAGED = f"{const.BEGIN} {_MARK} MANAGED"
_END_MANAGED = f"{const.END} {_MARK} MANAGED"
_BEGIN_EXCLUDED = f"{const.BEGIN} {_MARK} EXCLUDED"
_END_EXCLUDED = f"{const.END} {_MARK} EXCLUDED"


# FROM : https://github.com/yaml/pyyaml/issues/240#issuecomment-2093769180
def _yaml_multiline_string_pipe(
    dumper: yaml.dumper, data: dict
) -> yaml.dumper.Representer:
    if data.count("\n") > 0:
        data = "\n".join([
            line.rstrip() for line in data.splitlines()
        ])  # Remove any trailing spaces, then put it back together again
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _init_jinja_env(tpl_dir: str or None = None) -> jinja2.Environment:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    jinja_env = jinja2.Environment(
        extensions=[
            "jinja2.ext.i18n",
            "jinja2.ext.loopcontrols",
        ],
        keep_trailing_newline=True,
        trim_blocks=False,
        autoescape=True,
    )
    if tpl_dir:
        jinja_env.loader = jinja2.FileSystemLoader(tpl_dir)
    else:
        jinja_env.loader = jinja2.BaseLoader()

    return jinja_env


def _extract_content(content: str) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    contexts = {}
    curr_context = f"{_TEMPLATE}{_BEFORE}"
    contexts[curr_context] = ""
    re_begin_excluded = re.escape(f"{_BEGIN_EXCLUDED} ") + r"(\w+)"

    for line in content.splitlines():
        search = re.search(re_begin_excluded, line)
        if search:
            context_name = search.groups()[0]
            curr_context = context_name
            contexts[curr_context] = ""

        if re.search(re.escape(f"{_END_EXCLUDED} {curr_context}"), line):
            curr_context = f"{_TEMPLATE}{curr_context}"
            contexts[curr_context] = ""

        if not re.search(re.escape(_MARK), line):
            contexts[curr_context] += f"""{line}\n"""

    return contexts


def _extract_context(dest: str) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    contexts = {}
    curr_context = _BEFORE
    begin = f"{const.BEGIN} {_MARK}"
    end = f"{const.END} {_MARK}"
    re_begin_excluded = re.escape(f"{_BEGIN_EXCLUDED} ") + r"(\w+)"

    if not pathlib.Path(dest).exists():
        return contexts

    contexts[curr_context] = ""
    with pathlib.Path(dest).open(encoding="utf-8") as file:
        for line in file:
            search = re.search(re_begin_excluded, line)
            if search:
                context_name = search.groups()[0]
                curr_context = f"{context_name}"
                contexts[curr_context] = ""
            elif re.search(re.escape(begin), line):
                curr_context = f"{_TEMPLATE}{curr_context}"
                contexts[curr_context] = ""

            if re.search(re.escape(f"{_END_EXCLUDED} ") + r"(\w+)", line):
                curr_context = f"{_TEMPLATE}{curr_context}"
                contexts[curr_context] = ""
            elif re.search(re.escape(end), line):
                curr_context = _AFTER
                contexts[curr_context] = ""

            if not re.search(re.escape(_MARK), line):
                contexts[curr_context] += line

    # Remove empty contexts
    return {key: val for key, val in contexts.items() if val}


def _create_dest_dir(dst: pathlib.Path) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if not pathlib.Path(dst).parent.exists():
        log.debug("Creating directory %s", pathlib.Path(dst).parent)
        pathlib.Path(dst).mkdir(parents=True)


def _get_mark_comment(ft: str) -> [[str, str], [str, str]]:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    marks = {}
    for type_key, type_val in const.COMMENT_FILETYPE.items():
        if ft in type_val:
            begin = const.COMMENT_TYPE[type_key][const.BEGIN]
            end = const.COMMENT_TYPE[type_key][const.END]
            if end:
                end = f" {end}"
            marks[const.BEGIN] = f"{begin}"
            marks[const.END] = f"{end}"
            return marks
    return None, None


def _merge_context_content(contexts: dict, content: dict) -> dict:
    for key, _ in content.items():
        if key.startswith(_TEMPLATE):
            contexts[key] = content[key]
        if not key.startswith(_TEMPLATE) and key not in contexts:
            contexts[key] = content[key]


# pylint: disable=too-many-arguments
def render_file(
    config: dict,
    dst: str,
    content: str,
    ft: str,
    tpl_dir: pathlib.Path = "",
    is_static: bool = False,
) -> None:
    """Method that render any file from template.

    Args:
        config: Dotgit Sync configuration
        dst: Path to the destination file to render
        content: Content from template as multiline string
        ft: Filetype of destination files
        tpl_dir: Path to directory storing template files
        is_static: Boolean to specifiy if templates are static or none
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Processing %s", str(dst).replace(f"{config['git_root']}/", ""))

    _create_dest_dir(pathlib.Path(config["git_root"]) / dst)

    contexts = {}
    marks = {}
    if ft not in _FULL_FILE_TYPE:
        marks = _get_mark_comment(ft)
        contexts = _extract_context(dst)

    content = _extract_content(content)
    _merge_context_content(contexts, content)

    log.debug("Render %s", str(dst).replace(os.path.expandvars("${HOME}"), "~"))
    with pathlib.Path(dst).open("w", encoding="utf-8") as file:
        keys = list(contexts.keys())
        for idx, key in enumerate(keys):
            begin = f"{marks[const.BEGIN]}"
            end = f"{marks[const.BEGIN]}"
            if _TEMPLATE not in key:
                if key not in {_BEFORE, _AFTER}:
                    begin += f" {_BEGIN_EXCLUDED} {key}{marks[const.END]}"
                    end += f" {_END_EXCLUDED} {key}{marks[const.END]}"
                    file.write(f"{begin}\n")
                    file.write(contexts[key])
                    file.write(f"{end}\n")
                else:
                    file.write(contexts[key])
            else:
                begin += f" {_BEGIN_MANAGED}{marks[const.END]}"
                if key == f"{_TEMPLATE}{_BEFORE}":
                    file.write(f"{begin}\n")
                if is_static:
                    file.write(contexts[key])
                else:
                    file.write(
                        _init_jinja_env(tpl_dir)
                        .from_string(content[key])
                        .render(config)
                    )
                if idx == len(keys) - 1 or keys[idx + 1] == _AFTER:
                    end += f" {_END_MANAGED}{marks[const.END]}\n"
                else:
                    end = ""
                file.write(end)


def render_json(
    config: dict, dst: pathlib.Path, update: dict, is_yaml: bool = False
) -> None:
    """Method that render json or yaml file from template.

    Args:
        config: Dotgit Sync configuration
        dst: Path to the destination file to render
        update: Dictionnary from template
        is_yaml: Boolean to specifiy if templates are yaml or json files
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info("Merging %s to %s", dst, "YAML" if is_yaml else "JSON")

    _create_dest_dir(pathlib.Path(config["git_root"]) / dst)

    content = None
    if pathlib.Path(dst).is_file():
        with pathlib.Path(dst).open(encoding="utf-8") as file:
            content = yaml.safe_load(file) if is_yaml else json5.load(file)

    if isinstance(update, list):
        content = utils.merge_json_list(content, update)
    elif isinstance(update, dict):
        content = utils.merge_json_dict(content, update)

    with pathlib.Path(dst).open("w", encoding="utf-8") as file:
        if is_yaml:
            marks = _get_mark_comment(const.YAML)
            begin = f"{marks[const.BEGIN]} {_BEGIN_MANAGED}{marks[const.END]}"
            end = f"{marks[const.BEGIN]} {_END_MANAGED}{marks[const.END]}"
            file.write(f"{begin}\n")
            yaml.add_representer(str, _yaml_multiline_string_pipe)
            yaml.dump(
                content, file, indent=2, encoding="utf-8", sort_keys=False
            )
            file.write(end)
        else:
            json5.dump(
                content, file, indent=2, quote_keys=True, trailing_commas=False
            )
        file.write("\n")
