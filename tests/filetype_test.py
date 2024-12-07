#!/usr/bin/env python3
"""Module testing dotgit_sync.filetype."""

import inspect
import logging
import pathlib

from dotgit_sync import filetype
from dotgit_sync.utils import const


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestFiletype:
    """Collection suite testing filetype."""

    _script_path = pathlib.Path(__file__).parent

    @staticmethod
    def _ensure_all_exts_have_a_file(exts: list, files: list) -> None:
        """Ensure all extension define in constant have a testing file.

        Args:
            exts: list of extension
            files: list of files
        """
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Ensure there is at least one file for extension %s",
            str.join(",", exts),
        )
        log.info(
            "Files tested are %s", str.join(",", [file.name for file in files])
        )
        tmp_exts = []
        for file in files:
            ext = f".{file.name.split('.')[-1]}"
            if ext in exts and ext not in tmp_exts:  # pragma: no branch
                tmp_exts.append(ext)

        assert len(tmp_exts) == len(exts)

    @staticmethod
    def _assert_filetypes(files: list, target_ft: str) -> None:
        """Generic method to assert files correspond to a filetype.

        Args:
            files: list of files
            target_ft: filetype that should be associated to the files
        """
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should return markdown filetype for extensions %s",
            str.join(" ", const.FILETYPES[target_ft]),
        )

        for file in files:
            ft = filetype.get_filetype(file)
            assert ft == target_ft

    def _build_file_lists(
        self, target_ft: str
    ) -> (list[str], list[pathlib.Path]):
        """Build a list of file corresponding to a target filetype.

        Args:
            target_ft: string of a filetype
        """
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])

        exts = const.FILETYPES[target_ft]
        files = []
        fake_tpl_path = pathlib.Path(self._script_path) / "fake_templates"
        for tpl_dir in fake_tpl_path.iterdir():
            tpl_dir_path = pathlib.Path(fake_tpl_path) / tpl_dir / "all_types"
            for file_name in tpl_dir_path.iterdir():
                if "." + file_name.name.split(".")[-1] in exts:
                    files.append(pathlib.Path(tpl_dir_path) / file_name)
        return exts, files

    def _test_all_const_filetype(self, ft: str) -> None:
        """Generic method to test multiple files against a filetype.

        Args:
            ft: filetype to test
        """
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info(
            "Should return %s filetype for extensions %s",
            ft,
            str.join(" ", const.FILETYPES[ft]),
        )

        exts, files = self._build_file_lists(ft)
        self._ensure_all_exts_have_a_file(exts, files)
        self._assert_filetypes(files, ft)

    def test_all_const_filetypes(self) -> None:
        """Test all filetypes declared in constant."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should return filetype for const extensions")

        for ft in const.FILETYPES:
            self._test_all_const_filetype(ft)

    def test_all_test_files(self) -> None:
        """Test all filetypes in fake template folder statics."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Ensure all files in fake statics template have a filetype")

        fake_tpl_path = (
            self._script_path / "fake_templates" / const.TEMPLATES / "all_types"
        )
        for file_name in fake_tpl_path.iterdir():
            file_path = fake_tpl_path / file_name
            ft = filetype.get_filetype(file_path)
            assert ft in const.FILETYPES
