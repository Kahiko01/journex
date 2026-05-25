"""
Analytics endpoints package
"""

from .anonymous_tracking import router as anonymous_tracking_router
from .anonymous_dashboard import router as anonymous_dashboard_router

__all__ = [
    "anonymous_tracking_router",
    "anonymous_dashboard_router"
]
