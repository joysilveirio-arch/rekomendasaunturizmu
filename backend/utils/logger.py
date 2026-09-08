"""
Logging Configuration
"""

import logging
import sys
from datetime import datetime

# Create logger
_logger = None


def get_logger(name: str = None) -> logging.Logger:
    """Get a configured logger"""
    global _logger
    
    if _logger is None:
        _logger = logging.getLogger(name or "tourism_platform")
        _logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    
    if name:
        return logging.getLogger(name)
    return _logger


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger