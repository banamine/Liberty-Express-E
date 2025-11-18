"""
M3U Matrix Utilities Module
Contains helper functions, validators, and utilities
"""

# Import from validation module for backward compatibility
from .validation import (
    sanitize_filename,
    validate_url,
    validate_file_path,
    sanitize_input,
    SimpleCache,
    is_valid_m3u,
    download_and_cache_thumbnail,
    get_cached_thumbnail_stats
)

# Import dependency checker
from . import dependency_checker

__all__ = [
    'sanitize_filename',
    'validate_url',
    'validate_file_path',
    'sanitize_input',
    'SimpleCache',
    'is_valid_m3u',
    'download_and_cache_thumbnail',
    'get_cached_thumbnail_stats',
    'dependency_checker',
    'logger',
    'error_recovery'
]
