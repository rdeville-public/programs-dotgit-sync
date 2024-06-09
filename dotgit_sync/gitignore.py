#!/usr/bin/env python3
"""Generate gitignore from list of template."""

import inspect
import logging
import pathlib
import re

import requests

from . import const, render, repo


log = logging.getLogger(const.PKG_NAME)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"

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
    """Compute the gitignore file from dotgit config.

    Args:
        config: Dotgit Sync configuration
    """
    log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

    if const.GITIGNORE not in config:
        return

    gitignore_tpl = []
    if "templates" in config[const.GITIGNORE]:
        for tpl in config[const.GITIGNORE]["templates"]:
            gitignore_tpl.extend(GITIGNORE_CFG[tpl])

    if "query" in config[const.GITIGNORE]:
        for query in config[const.GITIGNORE]["query"]:
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

    dst = (
        pathlib.Path(repo.get_git_dir(pathlib.Path.cwd()))
        / f".{const.GITIGNORE}"
    )
    render.render_file(config, dst, tpl, const.GITIGNORE, is_static=True)
