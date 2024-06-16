#!/usr/bin/env python3

import inspect
import logging
import pathlib

from dotgit_sync.utils import json as utils
import pytest


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestUtilsJson:
    _script_path = pathlib.Path(__file__).parent
    _tpl_dir = _script_path / ".." / "fake_templates" / "statics" / "all_types"

    def _merge_list_diff_types(self, src, update):
        with pytest.raises(ValueError) as error:
            utils.merge_json_list(src, update)
        error_msg = f"Different types! {type(src[0])}, {type(update[0])}"
        assert error.match(error_msg)

    def _merge_list_first_empty(self, src, update):
        assert utils.merge_json_list(src, update) == update

    def _merge_list(self, src, update, target):
        assert utils.merge_json_list(src, update) == target

    def _merge_dict(self, src, update, target):
        assert utils.merge_json_dict(src, update) == target

    def test_merge_list_different_types(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should throw an error as item in lists are not same type")
        self._merge_list_diff_types(["foo"], [{"key": "value"}])
        self._merge_list_diff_types([["foo"]], [{"key": "value"}])
        self._merge_list_diff_types(["foo"], [["bar"]])

    def test_merge_list_first_empty(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should return the content of the second list as the first is empty"
        )
        self._merge_list_first_empty([], [{"key": "value"}])
        self._merge_list_first_empty([], ["foo"])
        self._merge_list_first_empty([], [["bar"]])

    def test_merge_list(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the merged content of the two list")
        self._merge_list(["foo"], ["bar"], ["foo", "bar"])
        self._merge_list(["foo", "baz"], ["foo", "bar"], ["foo", "baz", "bar"])
        self._merge_list(
            [{"key": "foo"}], [{"key": "bar"}], [{"key": "foo"}, {"key": "bar"}]
        )
        self._merge_list(
            [{"key": "foo"}, {"another_key": "baz"}],
            [{"key": "bar"}, {"key": "foo"}],
            [{"key": "foo"}, {"another_key": "baz"}, {"key": "bar"}],
        )
        self._merge_list([["foo"]], [["bar"]], [["foo"], ["bar"]])
        self._merge_list(
            [["foo", "baz"], ["bar"]],
            [["foo", "bar"]],
            [["foo", "baz"], ["bar"], ["foo", "bar"]],
        )
        self._merge_list(
            [["foo", "baz"], ["bar"]],
            [["foo", "bar"], ["foo", "baz"]],
            [["foo", "baz"], ["bar"], ["foo", "bar"]],
        )

    def test_merge_dict(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return the merged content of the two dictionary")
        self._merge_dict(None, {"key": "val"}, {"key": "val"})
        self._merge_dict({}, {"key": "val"}, {"key": "val"})
        self._merge_dict(
            {"key": "val"}, {"key": "another_val"}, {"key": "another_val"}
        )
        self._merge_dict(
            {"key": "val"},
            {"another_key": "another_val"},
            {"key": "val", "another_key": "another_val"},
        )
        self._merge_dict(
            {"key": "val", "list": ["foo"]},
            {"another_key": "another_val"},
            {"key": "val", "another_key": "another_val", "list": ["foo"]},
        )
        self._merge_dict(
            {"key": "val", "list": ["foo"], "dict": {"key": "val"}},
            {
                "another_key": "another_val",
                "list": ["bar"],
                "dict": {"key": "another_val"},
            },
            {
                "key": "val",
                "another_key": "another_val",
                "list": ["foo", "bar"],
                "dict": {"key": "another_val"},
            },
        )
        self._merge_dict(
            {"key": "val", "list": ["foo"], "dict": {"key": "val"}},
            {
                "key": 10,
                "another_key": "another_val",
                "list": ["bar"],
                "dict": {"key": "another_val"},
            },
            {
                "key": 10,
                "another_key": "another_val",
                "list": ["foo", "bar"],
                "dict": {"key": "another_val"},
            },
        )
