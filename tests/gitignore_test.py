#!/usr/bin/env python3

import inspect
import logging
import pathlib
import unittest
from unittest import mock

from dotgit_sync import gitignore
from dotgit_sync.utils import const


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    _script_path = pathlib.Path(__file__).parent

    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

    if args[0] == f"{gitignore.GITIGNORE_API}vs":
        target_content = pathlib.Path(
            _script_path / "fake_gitignore" / "query.vs.full.gitignore"
        ).read_text(encoding="utf-8")
        return MockResponse(target_content, 200)
    return MockResponse(None, 404)


class TestGitignore(unittest.TestCase):
    _script_path = pathlib.Path(__file__).parent
    _query_vs = {"gitignore": {"query": ["vs"]}}

    def test_build_query_param_from_templates(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from templates")
        for tpl in gitignore.GITIGNORE_CFG:
            config = {"gitignore": {"templates": [tpl]}}
            query_params = gitignore.build_query_param(config)
            self.assertEqual(query_params, gitignore.GITIGNORE_CFG[tpl])

    def test_build_query_param_from_query(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from query")
        for tpl in gitignore.GITIGNORE_CFG:
            config = self._query_vs
            query_params = gitignore.build_query_param(config)
            self.assertEqual(query_params, config["gitignore"]["query"])

    def test_build_query_param_from_templates_and_query(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should build query params from query and templates")
        config = {"gitignore": {"templates": ["base"], "query": ["python"]}}
        query_params = gitignore.build_query_param(config)
        self.assertEqual(
            query_params,
            gitignore.GITIGNORE_CFG["base"] + config["gitignore"]["query"],
        )

    # We patch 'requests.get' with our own method.
    # The mock object is passed in to our test case method.
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_full_content_simple_query(self, mock_get):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should get full gitignore content from query param")
        config = self._query_vs
        query_params = gitignore.build_query_param(config)
        _, content = gitignore.request_gitignore(query_params)
        target_content = pathlib.Path(
            self._script_path / "fake_gitignore" / "query.vs.full.gitignore"
        ).read_text(encoding="utf-8")
        self.assertEqual(content, target_content)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_wrong_query(self, mock_get):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return None if query params are wrong")
        config = {"gitignore": {"query": "false"}}
        query_params = gitignore.build_query_param(config)
        _, content = gitignore.request_gitignore(query_params)
        self.assertIsNone(content)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_cleaned_content_simple_query(self, mock_get):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should clean gitignore from full content")
        config = self._query_vs
        query_params = gitignore.build_query_param(config)
        url, content = gitignore.request_gitignore(query_params)
        content = gitignore.clean_gitignore(url, content)
        target_content = pathlib.Path(
            self._script_path / "fake_gitignore" / "query.vs.clean.gitignore"
        ).read_text(encoding="utf-8")

        self.assertEqual(content, target_content)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_not_in_config(self, mock_get):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return None as gitignore is not in config")
        config = {}
        self.assertIsNone(gitignore.process(config))

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_gitignore_rendering(self, mock_get):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should write clean gitignore file with dotgit block")
        outdir = pathlib.Path(self._script_path) / "fake_repo"
        config = {const.OUTDIR: str(outdir), "gitignore": {"query": ["vs"]}}
        gitignore.process(config)
        rendered_content = pathlib.Path(
            pathlib.Path(self._script_path) / "fake_repo" / ".gitignore"
        ).read_text(encoding="utf-8")
        target_content = pathlib.Path(
            self._script_path / "fake_gitignore" / "query.vs.render.gitignore"
        ).read_text(encoding="utf-8")
        self.assertEqual(rendered_content, target_content)
