"""
Centralised logging utilities for the reusable automation framework.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

import structlog

_IS_CONFIGURED = False


def configure_logging(log_mode: Optional[str] = None) -> None:
    """
Configure structlog-based logging for framework consumers.

Allows JSON (default) or console-friendly output via the LOG_MODE environment
variable or an explicit ``log_mode`` argument.
    """
    global _IS_CONFIGURED  # pylint: disable=global-statement

    if _IS_CONFIGURED and log_mode is None:
        return

    mode = (log_mode or os.getenv("LOG_MODE", "JSON")).upper()
    handler = logging.StreamHandler(sys.stdout)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        root_logger.addHandler(handler)

    root_logger.setLevel(logging.INFO)

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if mode == "LOCAL":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    _IS_CONFIGURED = True


def get_logger(name: Optional[str] = None):
    """
Return a structlog logger, ensuring logging is configured once.
    """
    configure_logging()
    return structlog.get_logger(name)
