#!/usr/bin/env python3

import inspect
import logging
import os
import pathlib
import unittest

from dotgit_sync import filetype
from dotgit_sync.utils import const


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestFiletype(unittest.TestCase):
    _script_path = pathlib.Path(__file__).parent

    def _ensure_all_exts_have_a_file(self, exts: list, files: list):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.warning(
            "Ensure there is at least one file for extension %s",
            str.join(",", exts),
        )
        log.warning(
            "Files tested are %s", str.join(",", [file.name for file in files])
        )
        tmp_exts = []
        for file in files:
            ext = f".{file.name.split('.')[-1]}"
            if ext in exts and ext not in tmp_exts:  # pragma: no branch
                tmp_exts.append(ext)

        self.assertEqual(len(tmp_exts), len(exts))

    def _assert_filetypes(self, files, target_ft):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should return markdown filetype for extensions %s",
            str.join(" ", const.FILETYPES[target_ft]),
        )
        for file in files:
            ft = filetype.get_filetype(file)
            self.assertEqual(ft, target_ft)

    def _build_file_lists(self, target_ft):
        exts = const.FILETYPES[target_ft]
        files = []
        fake_tpl_path = pathlib.Path(self._script_path) / "fake_templates"
        for tpl_dir in os.listdir(fake_tpl_path):
            tpl_dir_path = pathlib.Path(fake_tpl_path) / tpl_dir / "all_types"
            for file_name in os.listdir(tpl_dir_path):
                if "." + file_name.split(".")[-1] in exts:
                    files.append(pathlib.Path(tpl_dir_path) / file_name)
        return exts, files

    def _test_all_const_filetype(self, ft):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should return %s filetype for extensions %s",
            ft,
            str.join(" ", const.FILETYPES[ft]),
        )
        exts, files = self._build_file_lists(ft)
        self._ensure_all_exts_have_a_file(exts, files)
        self._assert_filetypes(files, ft)

    def test_all_const_filetypes(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return filetype for const extensions")
        for ft in const.FILETYPES:
            self._test_all_const_filetype(ft)

    def test_all_static_test_files(self):
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Ensure all files in fake statics template have a filetype")
        fake_tpl_path = (
            pathlib.Path(self._script_path)
            / "fake_templates"
            / "statics"
            / "all_types"
        )
        for file_name in os.listdir(fake_tpl_path):
            file_path = pathlib.Path(fake_tpl_path) / file_name
            ft = filetype.get_filetype(file_path)
            self.assertIn(ft, const.FILETYPES)
