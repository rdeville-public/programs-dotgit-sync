#!/usr/bin/env python3

import inspect
import logging
import os
import re

import requests

import const
import render
import repo

log = logging.getLogger(f"{const.PKG_NAME}")

GITIGNORE = "gitignore"
GITIGNORE_TPL_KEY = "templates"
GITIGNORE_CONFIG_KEY = "config"
GITIGNORE_API = "https://www.toptal.com/developers/gitignore/api/"
# List of available gitignore templates :
# https://github.com/toptal/gitignore/tree/master/templates
GITIGNORE_CFG = {
    "base": [
        "archive",
        "archives",
        "backup",
        "direnv",
        "dotenv",
        "emacs",
        "linux",
        "macos",
        "nohup",
        "ssh",
        "tags",
        "vim",
        "windows",
        "zsh",
        "vs",
        "visualstudio",
    ],
    "python": [
        "jupyternotebooks",
        "python",
        "venv",
    ],
    "javascript": [
        "angular",
        "extjs",
        "node",
        "nextjs",
        "nuxtjs",
        "prestashop",
        "vuejs",
        "vue",
        "storybookjs",
    ],
    "jsonnet": ["jsonnet"],
}


def process(config: dict) -> None:
    log.debug("%s:%s.%s()", os.path.basename(__file__), __name__, inspect.stack()[0][3])
    if GITIGNORE not in config:
        return

    gitignore_tpl = []
    if "templates" in config[GITIGNORE]:
        for tpl in config[GITIGNORE]["templates"]:
            gitignore_tpl.extend(GITIGNORE_CFG[tpl])

    if "query" in config[GITIGNORE]:
        for query in config[GITIGNORE]["query"]:
            gitignore_tpl.append(query)

    url = GITIGNORE_API + str.join(",", gitignore_tpl)
    tpl = requests.get(url, timeout=5).text
    # Catch Toptal URL
    url = re.search(r".+toptal.+", tpl, flags=re.MULTILINE).group(0)
    # Remove trailing tabs
    tpl = re.sub(r"[\t]+$", "", tpl, flags=re.MULTILINE)
    # Remove comment lines not followed by patterns
    tpl = re.sub(r"(^#.+\n)+\n", "", tpl, flags=re.MULTILINE)
    tpl = re.sub(r"(^###.+\n)+\n", "", tpl, flags=re.MULTILINE)
    tpl = url + "\n\n" + tpl

    dst = os.path.join(repo.get_git_dir(os.getcwd()), f".{GITIGNORE}")
    render.render_file(config, dst, tpl, "gitignore", is_static=True)
