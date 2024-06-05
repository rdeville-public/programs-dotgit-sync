# BEGIN DOTGIT-SYNC BLOCK MANAGED
"""Commit parser which looks for gitmojis to determine the type of commit"""

import requests
import logging
from typing import Tuple, NamedTuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseResult
from semantic_release.commit_parser.util import parse_paragraphs
from semantic_release.enums import LevelBump

logger = logging.getLogger(__name__)

GITMOJIS = "https://raw.githubusercontent.com/carloscuesta/gitmoji/master/packages/gitmojis/src/gitmojis.json"


def gitmoji_per_semver(
    gitmojis: str | dict, semver: str | None = None
) -> Tuple[str, ...]:
    global GITMOJIS
    if isinstance(GITMOJIS, str):
        GITMOJIS = requests.get(gitmojis).json()["gitmojis"]
    selected_gitmojis = []
    for gitmoji in GITMOJIS:
        if gitmoji["semver"] == semver:
            selected_gitmojis.append(gitmoji["emoji"])
            selected_gitmojis.append(gitmoji["code"])
    return selected_gitmojis


@dataclass
class GitmojiParserOptions(ParserOptions):
    # compute_default_gitmoji()
    major: Tuple[str, ...] = tuple(gitmoji_per_semver(GITMOJIS, "major"))
    minor: Tuple[str, ...] = tuple(gitmoji_per_semver(GITMOJIS, "minor"))
    patch: Tuple[str, ...] = tuple(gitmoji_per_semver(GITMOJIS, "patch"))
    other: Tuple[str, ...] = tuple(
        gitmoji_per_semver(
            GITMOJIS,
        )
    )
    default_bump_level: LevelBump = LevelBump.NO_RELEASE


class GitmojiCommitParser(CommitParser[ParseResult, GitmojiParserOptions]):
    """
    Parse a commit using an gitmoji in the subject line.
    When multiple gitmojis are encountered, the one with the highest bump
    level is used. If there are multiple gitmojis on the same level, the
    we use the one listed earliest in the configuration.
    If the message does not contain any known gitmojis, then the level to bump
    will be 0 and the type of change "Other". This parser never raises
    UnknownCommitMessageStyleError.
    Gitmojis are not removed from the description, and will appear alongside
    the commit subject in the changelog.
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = GitmojiParserOptions

    def parse(self, commit: Commit) -> ParseResult:
        all_gitmojis = (
            self.options.major
            + self.options.minor
            + self.options.patch
            + self.options.other
        )

        message = str(commit.message)
        subject = message.split("\n")[0]

        # Loop over gitmojis from most important to least important
        # Therefore, we find the highest level gitmoji first
        primary_gitmoji = "-"
        for gitmoji in all_gitmojis:
            if gitmoji in subject:
                primary_gitmoji = gitmoji
                break
        logger.debug("Selected %s as the primary gitmoji", primary_gitmoji)

        # Find which level this commit was from
        level_bump = LevelBump.NO_RELEASE
        if primary_gitmoji in self.options.major:
            level_bump = LevelBump.MAJOR
        elif primary_gitmoji in self.options.minor:
            level_bump = LevelBump.MINOR
        elif primary_gitmoji in self.options.patch:
            level_bump = LevelBump.PATCH

        # All gitmojis will remain part of the returned description
        descriptions = parse_paragraphs(message)
        # re.compile(r"\(![0-9]+\)").search(commit.message)
        return ParsedCommit(
            bump=level_bump,
            type=primary_gitmoji,
            scope="",
            descriptions=descriptions,
            breaking_descriptions=(
                descriptions[1:] if level_bump is LevelBump.MAJOR else []
            ),
            commit=commit,
        )

# END DOTGIT-SYNC BLOCK MANAGED
