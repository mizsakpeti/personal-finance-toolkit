"""Logging configuration and utilities for personal finance toolkit."""

import json
import logging
import logging.config
from pathlib import Path

import yaml


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging(config_path: str | None = None) -> None:
    """Configure logging from YAML configuration file.

    Args:
        config_path: Path to logging configuration file. If None, uses default.
    """
    if config_path is None:
        # Use default logging config in the package root
        config_path = str(Path(__file__).parent.parent / "logging_config.yaml")

    config_file = Path(config_path)
    if not config_file.exists():
        # Fall back to console logging if config file doesn't exist
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return

    try:
        with config_file.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    except Exception as e:
        fallback_logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        fallback_logger.warning(f"Failed to load logging config from {config_path}: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
