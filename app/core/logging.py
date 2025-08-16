"""
Logging configuration for the Shopify Insights application.
Provides structured logging with appropriate formatting and levels.
"""

import logging
import sys
from typing import Optional
from app.core.config import get_settings


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Setup application logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log message format string
    """
    settings = get_settings()
    
    # Use provided parameters or fall back to settings
    level = log_level or settings.log_level
    format_str = log_format or settings.log_format
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    # Set specific logger levels for external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Create application logger
    logger = logging.getLogger("shopify_insights")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Log configuration setup
    logger.info(f"Logging configured with level: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()
