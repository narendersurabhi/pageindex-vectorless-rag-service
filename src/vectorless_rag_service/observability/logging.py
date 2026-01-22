from __future__ import annotations

import logging
from typing import Any

import structlog

from vectorless_rag_service.config import settings


def setup_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if settings.observability.json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=logging.INFO)


def get_logger() -> structlog.BoundLogger:
    return structlog.get_logger()
