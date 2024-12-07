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

from .utils import const, jsonc as utils


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

_BEFORE = "before"
_AFTER = "after"
_TEMPLATE = "template"
_INDENT = "indent"
_CONTENT = "content"
_MARK = "DOTGIT-SYNC BLOCK"
_YAML_MERGED = "YAML_MERGED"
_ENFORCED = "ENFORCED"
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


def _extract_context_from_template(content: str, marks: dict) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    contexts = {}
    curr_context = f"{_TEMPLATE}{_BEFORE}"
    contexts[curr_context] = {}
    contexts[curr_context][_INDENT] = ""
    contexts[curr_context][_CONTENT] = ""

    re_begin_excluded = (
        r"(\s+)?"
        + re.escape(f"{marks[const.BEGIN]} {_BEGIN_EXCLUDED} ")
        + r"(\w+)"
    )

    for line in content.splitlines():
        search = re.search(re_begin_excluded, line)
        # If begin of exclude block in template file
        if re.search(re_begin_excluded, line):
            context_name = search.groups()[1]
            curr_context = context_name
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = search.groups()[0] or ""
            contexts[curr_context][_CONTENT] = ""

        # If end of exclude block, switch context
        if re.search(re.escape(f"{_END_EXCLUDED} {curr_context}"), line):
            curr_context = f"{_TEMPLATE}{curr_context}"
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = ""
            contexts[curr_context][_CONTENT] = ""

        if not re.search(re.escape(_MARK), line):
            contexts[curr_context][_CONTENT] += f"""{line}\n"""

    return contexts


def _extract_context_from_rendered_file(dest: str, marks: dict) -> dict:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    contexts = {}
    curr_context = _BEFORE
    begin = f"{const.BEGIN} {_MARK}"
    end = f"{const.END} {_MARK}"
    re_begin_excluded = (
        r"(\s+)?"
        + re.escape(f"{marks[const.BEGIN]} {_BEGIN_EXCLUDED} ")
        + r"(\w+)"
    )
    re_end_excluded = (
        r"(\s+)?"
        + re.escape(f"{marks[const.BEGIN]} {_END_EXCLUDED} ")
        + r"(\w+)"
    )

    re_begin = r"(\s+)?" + re.escape(f"{marks[const.BEGIN]} {begin}")

    if not pathlib.Path(dest).exists():
        return contexts

    contexts[curr_context] = {}
    contexts[curr_context][_INDENT] = ""
    contexts[curr_context][_CONTENT] = ""
    content = pathlib.Path(dest).read_text(encoding="utf-8")
    for line in content.splitlines():
        search = re.search(re_begin_excluded, line)
        if search:
            context_name = search.groups()[1]
            curr_context = context_name
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = search.groups()[0] or ""
            contexts[curr_context][_CONTENT] = ""
        elif re.search(re_begin, line):
            search = re.search(re_begin, line)
            curr_context = f"{_TEMPLATE}{curr_context}"
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = search.groups()[0] or ""
            contexts[curr_context][_CONTENT] = ""

        if re.search(re_end_excluded, line):
            search = re.search(re_end_excluded, line)
            curr_context = f"{_TEMPLATE}{curr_context}"
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = search.groups()[0] or ""
            contexts[curr_context][_CONTENT] = ""
        elif re.search(re.escape(end), line):
            curr_context = _AFTER
            contexts[curr_context] = {}
            contexts[curr_context][_INDENT] = ""
            contexts[curr_context][_CONTENT] = ""

        if not re.search(re.escape(_MARK), line):
            contexts[curr_context][_CONTENT] += f"""{line}\n"""

    # Remove empty contexts
    return {key: val for key, val in contexts.items() if val}


def _create_dest_dir(dst: pathlib.Path) -> None:
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if not pathlib.Path(dst).parent.exists():
        log.debug("Creating directory %s", pathlib.Path(dst).parent)
        pathlib.Path(dst).parent.mkdir(parents=True)


def _get_mark_comment(ft: str) -> dict:
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
    return marks


def _merge_contexts(contexts: dict, tpl_contexts: dict) -> dict:
    for key, _ in tpl_contexts.items():
        if key.startswith(_TEMPLATE) or key not in contexts:
            if key not in contexts:
                contexts[key] = {}
                contexts[key][_CONTENT] = tpl_contexts[key][_CONTENT]
                contexts[key][_INDENT] = tpl_contexts[key][_INDENT]
            else:
                contexts[key][_CONTENT] = tpl_contexts[key][_CONTENT]
                contexts[key][_INDENT] = tpl_contexts[key][_INDENT]
    return contexts


def _write_from_template(
    config: dict,
    content: str,
    dst: pathlib.Path,
    ft: str,
    tpl_dir: pathlib.Path = pathlib.Path(),
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
    log.info("Writing %s", str(dst).replace(f"{config[const.OUTDIR]}/", ""))

    marks = _get_mark_comment(ft)
    contexts = _extract_context_from_rendered_file(dst, marks)
    tpl_contexts = _extract_context_from_template(content, marks)

    contexts = _merge_contexts(contexts, tpl_contexts)
    _create_dest_dir(dst)

    log.debug("Render %s", str(dst).replace(os.path.expandvars("${HOME}"), "~"))
    with pathlib.Path(dst).open("w", encoding="utf-8") as file:
        keys = list(contexts.keys())
        for idx, key in enumerate(keys):
            if contexts[key][_INDENT]:
                begin = f"{contexts[key][_INDENT]}{marks[const.BEGIN]}"
                end = f"{contexts[key][_INDENT]}{marks[const.BEGIN]}"
            else:
                begin = f"{marks[const.BEGIN]}"
                end = f"{marks[const.BEGIN]}"

            if _TEMPLATE not in key:
                if key not in {_BEFORE, _AFTER}:
                    begin += f" {_BEGIN_EXCLUDED} {key}{marks[const.END]}"
                    end += f" {_END_EXCLUDED} {key}{marks[const.END]}"
                    file.write(f"{begin}\n")
                    file.write(contexts[key][_CONTENT])
                    file.write(f"{end}\n")
                else:
                    file.write(contexts[key][_CONTENT])
            else:
                begin += f" {_BEGIN_MANAGED}{marks[const.END]}"
                if key == f"{_TEMPLATE}{_BEFORE}":
                    file.write(f"{begin}\n")
                if is_static:
                    file.write(contexts[key][_CONTENT])
                else:
                    file.write(
                        _init_jinja_env(tpl_dir)
                        .from_string(contexts[key][_CONTENT])
                        .render(config)
                    )
                if idx == len(keys) - 1 or keys[idx + 1] == _AFTER:
                    end += f" {_END_MANAGED}{marks[const.END]}\n"
                else:
                    end = ""
                file.write(f"{end}")


def render_file(
    config: dict,
    dst: pathlib.Path,
    content: str,
    ft: str,
    tpl_dir: pathlib.Path = pathlib.Path(),
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
    log.info("Processing %s", str(dst).replace(f"{config[const.OUTDIR]}/", ""))

    _create_dest_dir(pathlib.Path(config[const.OUTDIR]) / dst)
    _write_from_template(config, content, dst, ft, tpl_dir, is_static)


def render_json(
    config: dict, dst: pathlib.Path, update: dict, ft: str, enforce: bool
) -> None:
    """Method that render json or yaml file from template.

    Args:
        config: Dotgit Sync configuration
        dst: Path to the destination file to render
        update: Dictionnary from template
        ft: filetype, either "yaml" or "json" is supported
        enforce: Boolean to force content remplacement if True, else will let
                 user new content in place
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
    log.info(
        "Merging %s to %s",
        str(dst).replace(f"{config[const.OUTDIR]}/", ""),
        "YAML" if ft == const.YAML else "JSON",
    )

    _create_dest_dir(dst)

    content = None
    if pathlib.Path(dst).is_file() and not enforce:
        with pathlib.Path(dst).open(encoding="utf-8") as file:
            log.error(ft)
            content = (
                yaml.safe_load(file) if ft == const.YAML else json5.load(file)
            )

    if isinstance(update, dict):
        content = utils.merge_json_dict(content, update)
    else:  # isinstance(update, list)
        content = utils.merge_json_list(content, update)

    with pathlib.Path(dst).open("w", encoding="utf-8") as file:
        if ft == const.YAML:
            marks = _get_mark_comment(const.YAML)
            begin = (
                f"{marks[const.BEGIN]} {_BEGIN_MANAGED}{marks[const.END]} "
                + f"{_YAML_MERGED}"
            )
            end = (
                f"{marks[const.BEGIN]} {_END_MANAGED}{marks[const.END]} "
                + f"{_YAML_MERGED}"
            )
            if enforce:
                begin += f"_{_ENFORCED}"
                end += f"_{_ENFORCED}"
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
