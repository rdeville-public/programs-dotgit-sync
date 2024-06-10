#!/usr/bin/env python3
"""Set of constants use by dotgit sync."""

PKG_NAME = "dotgit"

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
JS = "javascript"
JSON = "json"
J2 = "jinja2"
LICENSE = "licenses"
MD = "markdown"
PY = "python"
TOML = "toml"
SH = "shell"
TS = "typescript"
TXT = "text"
YAML = "yaml"

# FILETYPES WITH EXTS
FILETYPES = {
    GITIGNORE: [".gitignore"],
    EDITORCFG: [".editorconfig"],
    HBS: [".hbs"],
    JS: [".js"],
    J2: [".j2"],
    JSON: [".jsonc", ".json"],
    MD: [".md"],
    PY: [".py"],
    SH: [".sh", ".bash", ".zsh"],
    TOML: [".toml"],
    TS: [".ts"],
    PLAIN: [".txt", ".in", ".envrc"],
    YAML: [".yml", ".yaml"],
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
        TOML,
        LICENSE,
        SH,
    ],
    SLASH_STAR: [JS, TS],
    XML: [MD],
    CURLY_HASHTAG: [J2],
}

# Config Options
MERGE = "merge"
NONE = "none"
ALL = "all"
ONLY = "only"

# CONST STORING DEFAULT DOTGIT CONFIG
DOTGIT = {PKG_NAME: {YAML: {MERGE: NONE}}}
