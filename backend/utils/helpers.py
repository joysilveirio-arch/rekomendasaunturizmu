"""
Helper Functions
"""

from datetime import datetime
from typing import Optional, Any


def format_date(date: Optional[datetime], format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object to string"""
    if date is None:
        return ""
    return date.strftime(format)


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert a value to string"""
    if value is None:
        return default
    return str(value)


def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to a maximum length"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."