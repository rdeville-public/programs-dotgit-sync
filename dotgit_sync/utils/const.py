#!/usr/bin/env python3
"""Set of constants use by dotgit sync."""

import ordered_set


PKG_NAME = "dotgit_sync"

# LOGGER
# This const variable will be set by config_logger in logger.py
LOG = None

# TEMPLATE MARKS
BEGIN = "BEGIN"
END = "END"

# FILETYPES
PLAIN = "plain"
EDITORCFG = "editorconfig"
GITIGNORE = "gitignore"
HBS = "handlebars"
J2 = "jinja2"
JAVA = "java"
JS = "javascript"
JSON = "json"
LICENSES = "licenses"  # Also a dotgit config key
NIX = "nix"
MD = "markdown"
PY = "script.python"
TOML = "toml"
SH = "shellscript"
TS = "typescript"
PLAIN = "plain"
YAML = "yaml"

# FILETYPES WITH EXTS
FILETYPES = {
    GITIGNORE: [".gitignore", ".markdownlintignore", ".yamlignore"],
    EDITORCFG: [".editorconfig"],
    HBS: [".hbs"],
    J2: [".j2"],
    JAVA: [],
    JS: [],
    JSON: [".jsonc", ".json"],
    NIX: [".nix"],
    MD: [".md", ".markdown", ".mkdown"],
    PY: [".py"],
    SH: [".sh", ".bash", ".zsh"],
    TOML: [".toml"],
    TS: [".ts"],
    PLAIN: [".txt", ".in", ".envrc"],
    YAML: [".yml", ".yaml", ".yamllint"],
}

# COMMENT TYPE NAME
HASHTAG = "HASHTAG"
XML = "XML"
DOUBLE_SLASH = "DOUBLE_SLASH"
SLASH_STAR = "SLASH_STAR"
CURLY_HASHTAG = "CURLY_HASHTAG"

# COMMENT TYPE
COMMENT_TYPE = {
    HASHTAG: {BEGIN: "#", END: ""},
    XML: {BEGIN: "<!--", END: "-->"},
    DOUBLE_SLASH: {BEGIN: "//", END: ""},
    SLASH_STAR: {BEGIN: "/*", END: "*/"},
    CURLY_HASHTAG: {BEGIN: "{#-", END: "-#}"},
}

# COMMENT_TYPE WITH FILETYPES
COMMENT_FILETYPE = {
    HASHTAG: [
        PY,
        YAML,
        GITIGNORE,
        EDITORCFG,
        PLAIN,
        NIX,
        TOML,
        LICENSES,
        SH,
    ],
    SLASH_STAR: [JS, TS, JAVA],
    XML: [MD],
    CURLY_HASHTAG: [J2],
}

# KEYS USED IN CONFIG FILES
DOTGIT = "dotgit"
MERGE = "merge"
ENFORCE = "enforce"
METHOD = "method"
NONE = "none"
ALL = "all"
ONLY = "only"
OUTDIR = "outdir"
DATE = "date"
FIRST_YEAR = "first_year"
CURR_YEAR = "current_year"
SOURCE = "source"
GIT = "git"
URL = "url"
REF = "ref"
PATH = "path"
MAINTAINERS = "maintainers"
NAME = "name"
MAIL = "mail"
COPYRIGHT = "copyright"
OWNER = "owner"
EMAIL = "email"
SECONDARIES = "secondaries"
PRIMARY = "primary"
TEMPLATES = "templates"
STATICS = "statics"

# NAME OF MIGRATIONS DIRECTORY
MIGRATIONS = "migrations"
VERSION = "version"
CFG_VERSIONS = ordered_set.OrderedSet(["v0", "v1alpha1"])
