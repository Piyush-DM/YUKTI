"""Logging initialization for DAALE infrastructure utilities."""

from __future__ import annotations

import logging


LOGGER_NAME = "daale"


def initialize_logging(level: int = logging.INFO) -> logging.Logger:
    """Initialize and return the package logger.

    The function configures handler state only. It does not emit reasoning,
    report, execution, or runtime logs.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)

    return logger
