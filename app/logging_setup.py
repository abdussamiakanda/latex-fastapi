import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from pathlib import Path
from app.config import LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT


_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    path = Path(LOG_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("latex_api.access")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(
            path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    _logger = logger
    return logger


def log_call(entry: dict) -> None:
    record = {"time": datetime.now(timezone.utc).isoformat()}
    record.update(entry)
    get_logger().info(json.dumps(record, ensure_ascii=False, default=str))
