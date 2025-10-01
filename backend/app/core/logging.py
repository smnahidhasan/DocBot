import logging
import logging.config
import os
from datetime import datetime
import json
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry["ip_address"] = record.ip_address
        if hasattr(record, 'user_agent'):
            log_entry["user_agent"] = record.user_agent
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'response_time'):
            log_entry["response_time"] = record.response_time

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging():
    """Configure logging for the application"""

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Get log level from environment variable
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file_info": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/info.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "file_access": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file_info", "file_error"],
                "propagate": False,
            },
            "app": {
                "level": log_level,
                "handlers": ["console", "file_info", "file_error"],
                "propagate": False,
            },
            "access": {
                "level": "INFO",
                "handlers": ["file_access"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file_access"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file_error"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    # Log startup message
    logger = logging.getLogger("app")
    logger.info(f"Logging configured with level: {log_level}")


# Custom logger for access logs
def get_access_logger():
    return logging.getLogger("access")


# Function to add context to log records
def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """Log message with additional context"""
    record = logger.makeRecord(
        logger.name, level, "", 0, message, (), None
    )
    for key, value in context.items():
        setattr(record, key, value)
    logger.handle(record)

