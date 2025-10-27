import logging
import sys

from compile_utils.constants import LOGGER_NAME


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    # Send DEBUG - WARNING to stdout and ERROR to stderr
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.addFilter(lambda record: record.levelno <= logging.WARNING)
    errorHandler = logging.StreamHandler(sys.stderr)
    errorHandler.setLevel(logging.ERROR)

    logger.addHandler(handler)
    logger.addHandler(errorHandler)

    return logger
