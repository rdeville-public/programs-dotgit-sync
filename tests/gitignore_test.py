#!/usr/bin/env python3
"""Module testing dotgit.gitignore."""

from dataclasses import dataclass
import inspect
import logging
import pathlib
from unittest import mock

from dotgit_sync import gitignore
from dotgit_sync.utils import const


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args: dict, **kwargs: dict):  # noqa: ARG001, ANN201
    """Method mocking request to gitignore.io."""
    script_path = pathlib.Path(__file__).parent

    @dataclass
    class MockResponse:
        def __init__(self, text: str, status_code: int) -> None:
            self.text = text
            self.status_code = status_code

    if args[0] == f"{gitignore.GITIGNORE_API}vs":
        target_content = (
            script_path / "fake_gitignore" / "query.vs.full.gitignore"
        ).read_text(encoding="utf-8")
        return MockResponse(target_content, 200)
    return MockResponse(None, 404)


class TestGitignore:
    """Collection suite to test gitignore."""

    _script_path = pathlib.Path(__file__).parent
    _config = {"gitignore": {"query": ["vs"]}}  # noqa : RUF012

    @staticmethod
    def test_build_query_param_from_templates() -> None:
        """Test way query parameters are build from template key in config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from templates")

        for tpl in gitignore.GITIGNORE_CFG:
            config = {"gitignore": {"templates": [tpl]}}
            query_params = gitignore.build_query_param(config)
            assert query_params == gitignore.GITIGNORE_CFG[tpl]

    def test_build_query_param_from_query(self) -> None:
        """Test way query parameters are build from query key in config."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from query")

        for _ in gitignore.GITIGNORE_CFG:
            query_params = gitignore.build_query_param(self._config)
            assert query_params == self._config["gitignore"]["query"]

    @staticmethod
    def test_build_query_param_from_templates_and_query() -> None:
        """Test way query parameters are built from both gitignore keys in config."""  # noqa: E501
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from query and templates")

        config = {"gitignore": {"templates": ["base"], "query": ["python"]}}
        query_params = gitignore.build_query_param(config)
        assert query_params == (
            gitignore.GITIGNORE_CFG["base"] + config["gitignore"]["query"]
        )

    # We patch 'requests.get' with our own method.
    # The mock object is passed in to our test case method.
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_full_content_simple_query(self, mock_get) -> None:  # noqa: ANN001, ARG002
        """Test gitignore request from simple query."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should get full gitignore content from query param")

        query_params = gitignore.build_query_param(self._config)
        _, content = gitignore.request_gitignore(query_params)
        target_content = pathlib.Path(
            self._script_path / "fake_gitignore" / "query.vs.full.gitignore"
        ).read_text(encoding="utf-8")
        assert content == target_content

    @staticmethod
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_wrong_query(mock_get) -> None:  # noqa: ANN001, ARG004
        """Test gitignore use wrong query parameter."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return None if query params are wrong")

        config = {"gitignore": {"query": "false"}}
        query_params = gitignore.build_query_param(config)
        _, content = gitignore.request_gitignore(query_params)
        assert content is None

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_cleaned_content_simple_query(self, mock_get) -> None:  # noqa: ANN001, ARG002
        """Test gitignore cleaning."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should clean gitignore from full content")

        query_params = gitignore.build_query_param(self._config)
        url, content = gitignore.request_gitignore(query_params)
        content = gitignore.clean_gitignore(url, content)
        target_content = pathlib.Path(
            self._script_path / "fake_gitignore" / "query.vs.clean.gitignore"
        ).read_text(encoding="utf-8")

        assert content == target_content

    @staticmethod
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_not_in_config(mock_get) -> None:  # noqa: ANN001, ARG004
        """Ensure that no gitignore in config is handled."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return None as gitignore is not in config")

        config = {}
        assert gitignore.process(config) is None

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_rendering(self, mock_get) -> None:  # noqa: ANN001, ARG002
        """Ensure gitignore rendering."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write clean gitignore file with dotgit block")

        outdir = self._script_path / "fake_repo"
        config = {const.OUTDIR: str(outdir), "gitignore": {"query": ["vs"]}}
        gitignore.process(config)
        assert (self._script_path / "fake_repo" / ".gitignore").read_text(
            encoding="utf-8"
        ) == (
            self._script_path / "fake_gitignore" / "query.vs.render.gitignore"
        ).read_text(encoding="utf-8")
