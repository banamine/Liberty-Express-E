"""
ScheduleFlow API Layer - Week 1 Modularization

REST API endpoints for schedule management, channel operations, and file handling.
"""

from .server import create_app, get_app_instance

__all__ = ['create_app', 'get_app_instance']
