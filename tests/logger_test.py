#!/usr/bin/env python3
"""Module testing dotgit.logger."""

from collections import namedtuple
import inspect
import logging
import pathlib

from dotgit_sync import logger
import pytest


log = logging.getLogger(__name__)
_LOG_TRACE = f"{pathlib.Path(__file__).name}:{__name__}"


class TestLogger:
    """Collection testing logger."""

    Args = namedtuple("Args", ["verbose", "log_format"])

    def _set_logger(
        self,
        logger_name: str,
        verbosity: int = 0,
        log_format: str = "string",
    ) -> logging.Logger:
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        test_log = logging.getLogger(logger_name)
        args = self.Args(verbosity, log_format)
        logger.init_logger(args, test_log)
        return test_log

    def test_init_logger_string(self) -> None:
        """Testing logger output format set to string."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should accept format 'string', 'String' and 'STRING'")

        test_log = self._set_logger(inspect.stack()[0][3], log_format="string")
        assert test_log.level == logging.WARNING

        test_log = self._set_logger(inspect.stack()[0][3], log_format="String")
        assert test_log.level == logging.WARNING

        test_log = self._set_logger(inspect.stack()[0][3], log_format="STRING")
        assert test_log.level == logging.WARNING

    def test_init_logger_json(self) -> None:
        """Testing logger output format set to json."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should accept format 'json', 'Json' and 'JSON'")

        test_log = self._set_logger(inspect.stack()[0][3], log_format="json")
        assert test_log.level == logging.WARNING

        test_log = self._set_logger(inspect.stack()[0][3], log_format="Json")
        assert test_log.level == logging.WARNING

        test_log = self._set_logger(inspect.stack()[0][3], log_format="JSON")
        assert test_log.level == logging.WARNING

    def test_init_logger_verbosity(self) -> None:
        """Testing logger output verbosity depending of number of arguments."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should set verbosity to INFO for 1 '-v'")

        test_log = self._set_logger(inspect.stack()[0][3], 1)
        assert test_log.level == logging.INFO

        test_log = self._set_logger(inspect.stack()[0][3], 2)
        assert test_log.level == logging.DEBUG

        test_log = self._set_logger(inspect.stack()[0][3], 3)
        assert test_log.level == logging.DEBUG

    def test_init_logger_wrong_level(self) -> None:
        """Testing logger throw an error if negative verbosity level."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should raise a LookupError if negative verbosity")

        verbosity = -1
        with pytest.raises(LookupError) as error:
            self._set_logger(inspect.stack()[0][3], verbosity)
        assert f"Verbosity of {verbosity} is not valid." in str(error.value)

    def test_init_logger_wrong_format(self) -> None:
        """Testing logger throw an error if wrong verbosity format."""
        log.debug("%s.%s()", _LOG_TRACE, inspect.stack()[0][3])
        log.info("Should raise a LookupError if invalid log format")

        with pytest.raises(LookupError) as error:
            self._set_logger(inspect.stack()[0][3], log_format="wrong")
        assert "Log format should be either `json` or `string`." in str(
            error.value
        )
