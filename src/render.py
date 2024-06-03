#!/usr/bin/env python3

import inspect
import io
import json
import logging
import os
import re

import jinja2

import const
import utils

log = logging.getLogger(f"{const.PKG_NAME}")

_FULL_FILE_TYPE = ["plain", "handlebars", "unknown"]
_BEFORE = "before"
_AFTER = "after"
_BEGIN = "BEGIN"
_END = "END"
_TEMPLATE = "template"
_MARK = "DOTGIT-SYNC BLOCK"
_MANAGED = "MANAGED"
_EXCLUDED = "EXCLUDED"
_MARK_COMMENT_TYPE = {
    "HASHTAG": {_BEGIN: "#", _END: ""},
    "XML": {_BEGIN: "<!--", _END: "-->"},
    "DOUBLE_SLASH": {_BEGIN: "//", _END: ""},
    "SLASH_STAR": {_BEGIN: "/*", _END: "*/"},
    "CURLY_HASHTAG": {_BEGIN: "{#-", _END: "-#}"},
}
_MARK_COMMENT_FILETYPE = {
    "HASHTAG": [
        "python",
        "yaml",
        "gitignore",
        "editorconfig",
        "text",
        "yaml",
        "toml",
        "license",
    ],
    "SLASH_STAR": ["javascript", "typescript"],
    "XML": [
        "markdown",
    ],
    "CURLY_HASHTAG": ["jinja2"],
}


def _init_jinja_env(tpl_dir: str or None = None) -> jinja2.Environment:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    jinja_env = jinja2.Environment(
        extensions=[
            "jinja2.ext.i18n",
            "jinja2.ext.loopcontrols",
        ],
        keep_trailing_newline=True,
        trim_blocks=False,
        autoescape=False,
    )
    if tpl_dir:
        jinja_env.loader = jinja2.FileSystemLoader(tpl_dir)
    else:
        jinja_env.loader = jinja2.BaseLoader()

    return jinja_env


def _extract_content(content: str) -> dict:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    contexts = {}
    curr_context = f"{_TEMPLATE}{_BEFORE}"
    contexts[curr_context] = ""
    begin = f"{_BEGIN} {_MARK}"
    end = f"{_END} {_MARK}"

    for line in content.splitlines():

        if re.search(f"{begin} {_EXCLUDED} (\w+)", line):
            context_name = re.search(f"{begin} {_EXCLUDED} (\w+)", line).groups()[0]
            curr_context = context_name
            contexts[curr_context] = ""

        if re.search(f"{end} {_EXCLUDED} {curr_context}", line):
            curr_context = f"{_TEMPLATE}{curr_context}"
            contexts[curr_context] = ""

        if not re.search(f"{_MARK}", line):
            contexts[curr_context] += f"""{line}\n"""

    return contexts


def _extract_context(dest: str) -> dict:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    contexts = {}
    curr_context = _BEFORE
    begin = f"{_BEGIN} {_MARK}"
    end = f"{_END} {_MARK}"

    if not os.path.exists(dest):
        return contexts

    contexts[curr_context] = ""
    with open(dest, "r", encoding="utf-8") as file:
        for line in file:

            if re.search(f"{begin} {_EXCLUDED} (\w+)", line):
                context_name = re.search(f"{begin} {_EXCLUDED} (\w+)", line).groups()[0]
                curr_context = f"{context_name}"
                contexts[curr_context] = ""
            elif re.search(f"{begin}", line):
                curr_context = f"{_TEMPLATE}{curr_context}"
                contexts[curr_context] = ""

            if re.search(f"{end} {_EXCLUDED} (\w+)", line):
                curr_context = f"{_TEMPLATE}{curr_context}"
                contexts[curr_context] = ""
            elif re.search(f"{end}", line):
                curr_context = _AFTER
                contexts[curr_context] = ""

            if not re.search(f"{_MARK}", line):
                contexts[curr_context] += line

    # Remove empty contexts
    final_contexts = {key: val for key, val in contexts.items() if val != ""}

    return final_contexts


def _create_dest_dir(dst: os.path) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])

    if not os.path.exists(os.path.dirname(dst)):
        log.debug("Creating directory %s", os.path.dirname(dst))
        os.makedirs(os.path.dirname(dst))


def _get_mark_comment(ft: str) -> [[str, str], [str, str]]:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    marks = {}
    for type_key, type_val in _MARK_COMMENT_FILETYPE.items():
        if ft in type_val:
            begin = _MARK_COMMENT_TYPE[type_key][_BEGIN]
            end = _MARK_COMMENT_TYPE[type_key][_END]
            if end != "":
                end = f" {end}"
            marks[_BEGIN] = f"{begin}"
            marks[_END] = f"{end}"
            return marks
    return None, None


def _merge_context_content(contexts: dict, content: dict) -> dict:
    for key, _ in content.items():
        if key.startswith(_TEMPLATE):
            contexts[key] = content[key]
        if not key.startswith(_TEMPLATE) and key not in contexts:
            contexts[key] = content[key]


def render_file(
    config: dict,
    dst: str,
    content: str,
    ft: str,
    tpl_dir: os.path = False,
    is_static: bool = False,
):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    log.info("Processing %s", dst.replace(f"{config["git_root"]}/", ""))

    _create_dest_dir(os.path.join(config["git_root"], dst))

    if ft not in _FULL_FILE_TYPE:
        marks = _get_mark_comment(ft)
        contexts = _extract_context(dst)

    content = _extract_content(content)
    _merge_context_content(contexts, content)

    log.debug("Render %s", dst.replace(os.path.expandvars("${HOME}"), "~"))
    with open(dst, "w", encoding="utf-8") as file:
        keys = list(contexts.keys())
        for idx, key in enumerate(keys):
            begin = f"{marks[_BEGIN]} {_BEGIN} {_MARK}"
            end = f"{marks[_BEGIN]} {_END} {_MARK}"
            if is_static:
                begin += f" {_MANAGED}{marks[_END]}"
                end += f" {_MANAGED}{marks[_END]}"
                file.write(f"{begin}\n{contexts[key]}{end}")
            elif _TEMPLATE not in key:
                if key not in [_BEFORE, _AFTER]:
                    begin += f" {_EXCLUDED} {key}{marks[_END]}"
                    end += f" {_EXCLUDED} {key}{marks[_END]}"
                    file.write(f"{begin}\n{contexts[key]}{end}")
                else:
                    file.write(contexts[key])
            else:
                begin += f" {_MANAGED}{marks[_END]}"
                if key == f"{_TEMPLATE}{_BEFORE}":
                    file.write(f"{begin}\n")
                file.write(
                    _init_jinja_env(tpl_dir).from_string(content[key]).render(config)
                )
                file.write("\n")
                if idx == len(keys) - 1:
                    end += f" {_MANAGED}{marks[_END]}"
                elif keys[idx + 1] == _AFTER:
                    end += f" {_MANAGED}{marks[_END]}\n"
                else:
                    end = ""
                file.write(end)


def render_json(config: dict, dst: os.path, update) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    log.info("Merging JSON to %s", dst)

    _create_dest_dir(os.path.join(config["git_root"], dst))

    content = None
    if os.path.isfile(dst):
        with open(dst, "r", encoding="utf-8") as file:
            content = json.load(file)

    if isinstance(update, list):
        content = utils.merge_json_list(content, update)
    elif isinstance(update, dict):
        content = utils.merge_json_dict(content, update)

    with open(dst, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=2)
        file.write("\n")
