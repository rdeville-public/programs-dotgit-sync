#!/usr/bin/env python3

import inspect
import logging
import os

import magic

import const

log = logging.getLogger(f"{const.PKG_NAME}")

_TYPE = {
    "handlebars": [".hbs"],
    "javascript": [".js"],
    "markdown": [".md"],
    "text": [".txt"],
    "typescript": [".ts"],
    "yaml": [".yml", ".yaml"],
    "editorconfig": [".editorconfig"],
    "toml": [".toml"],
    "jinja2": [".j2"],
    "python": [".py"],
    "json": [".jsonc", ".json"],
}


def get_filetype(filename: str) -> str | bool:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    ft = magic.from_file(filename, mime=True).split("/")[-1]
    if ft != "plain" and not ft.startswith("x-"):
        return ft
    ext = f".{filename.split('.')[-1]}"
    for ft, exts in _TYPE.items():
        if ext in exts:
            return ft
    return "unknown"
