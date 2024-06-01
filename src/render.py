#!/usr/bin/env python3

import inspect
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
_MARK = "DOTGIT-SYNC MANAGED BLOCK"
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


def _init_jinja_env(tpl_dir: str) -> jinja2.Environment:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    jinja_env = jinja2.Environment(
        extensions=[
            "jinja2.ext.i18n",
            "jinja2.ext.loopcontrols",
        ],
        keep_trailing_newline=True,
        trim_blocks=False,
        autoescape=False,
        loader=jinja2.FileSystemLoader(tpl_dir),
    )

    return jinja_env


def _extract_context(dest: str) -> dict:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    context = {_BEFORE: "", _AFTER: ""}
    curr_context = _BEFORE
    marks = {}
    marks[_BEGIN] = f"{_BEGIN} {_MARK}"
    marks[_END] = f"{_END} {_MARK}"

    if os.path.exists(dest):
        with open(dest, "r", encoding="utf-8") as file:
            for line in file:
                if re.search(f"{marks[_BEGIN]}", line):
                    curr_context = "template"
                if curr_context in context:
                    context[curr_context] += line
                if re.search(f"{marks[_END]}", line):
                    curr_context = _AFTER
    return context


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
            marks[_BEGIN] = f"{begin} {_BEGIN} {_MARK}{end}"
            marks[_END] = f"{begin} {_END} {_MARK}{end}"
            return marks
    return None, None


def render_file(
    config: dict,
    dst: str,
    content: str,
    ft: str,
    is_static: bool = False,
):
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    log.info("Start processing %s of filetype %s", os.path.basename(dst), ft)

    _create_dest_dir(os.path.join(config["git_root"], dst))

    marks = {}
    context = {}
    if ft not in _FULL_FILE_TYPE:
        marks = _get_mark_comment(ft)
        context = _extract_context(dst)

    log.debug("Render %s", dst)
    with open(dst, "w", encoding="utf-8") as file:
        if context is not None and _BEFORE in context and context[_BEFORE]:
            file.write(context[_BEFORE])
            file.write("\n")
        if marks is not None and _BEGIN in marks and marks[_BEGIN]:
            file.write(marks[_BEGIN])
            file.write("\n")

        if is_static:
            file.write(content)
            file.write("\n")
        else:
            file.write(jinja2.Template(content).render(config))
            file.write("\n")

        if marks is not None and _END in marks and marks[_END]:
            file.write(marks[_END])
            file.write("\n")
        if context is not None and _AFTER in context and context[_AFTER]:
            file.write(context[_AFTER])
            file.write("\n")


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
