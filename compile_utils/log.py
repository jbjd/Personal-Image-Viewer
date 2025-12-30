"""Logging setup."""

import logging
import sys

LOGGER_NAME: str = "personal_logger"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Sets up logger with levels below error going to stdout and
    error and fatal going to stderr.

    :param level: Logging level.
    :returns: The setup logger."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    # Send DEBUG - WARNING to stdout and ERROR to stderr
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.addFilter(lambda record: record.levelno <= logging.WARNING)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)

    logger.addHandler(handler)
    logger.addHandler(error_handler)

    return logger
