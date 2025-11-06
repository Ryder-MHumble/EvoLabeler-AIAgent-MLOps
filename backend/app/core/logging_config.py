"""
Logging configuration for structured logging.

This module sets up a structured logging system with JSON formatting
for production and human-readable formatting for development.
"""

import logging
import sys
from typing import Any
from datetime import datetime

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured log messages.
    
    In production, outputs JSON format for easy parsing.
    In development, outputs human-readable format with colors.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured message."""
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()

        # Extract extra fields
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__ and k != "timestamp"
        }

        if settings.debug:
            # Human-readable format for development
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            reset = self.COLORS["RESET"]
            
            msg = (
                f"{color}[{record.levelname}]{reset} "
                f"{record.timestamp} - {record.name} - {record.getMessage()}"
            )
            
            if extra_fields:
                msg += f" | {extra_fields}"
            
            if record.exc_info:
                msg += f"\n{self.formatException(record.exc_info)}"
            
            return msg
        else:
            # JSON format for production
            import json
            
            log_data: dict[str, Any] = {
                "timestamp": record.timestamp,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra fields
            if extra_fields:
                log_data["extra"] = extra_fields
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure logging for the application.
    
    This should be called once during application startup.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    
    # Set formatter
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level,
            "debug_mode": settings.debug,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name, typically __name__ of the module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


