"""Structured JSON logging configuration using structlog."""

import logging
import sys
import structlog
from typing import Optional

from app.config import settings


def configure_logging(log_level: Optional[str] = None):
    """Configure structured JSON logging.

    Args:
        log_level: Override log level (default: from settings)
    """
    level = log_level or settings.log_level

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Bound structlog logger
    """
    return structlog.get_logger(name)
