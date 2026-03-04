"""
Anonymous Dashboard API Endpoints
For viewing anonymous tracking statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.session import get_db
from app.services.analytics.anonymous.anonymous_stats import AnonymousStatsService
from app.api.deps.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/anonymous-dashboard", tags=["anonymous-dashboard"])
stats_service = AnonymousStatsService()

# Simple auth check - only allow specific admin users
# In production, you'd want proper admin authentication
ADMIN_USERNAMES = ["testuser", "admin"]  # Add your admin usernames here

@router.get("/stats")
async def get_anonymous_stats(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get anonymous statistics (admin only)"""
    # Check if user is admin
    if current_user.username not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = stats_service.get_dashboard_stats(db, days)
        return stats
    except Exception as e:
        logger.error(f"Error getting anonymous stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime")
async def get_realtime_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time anonymous statistics (admin only)"""
    if current_user.username not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = stats_service.get_realtime_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting realtime stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features/{feature_name}")
async def get_feature_details(
    feature_name: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed stats for a specific feature (admin only)"""
    if current_user.username not in ADMIN_USERNAMES:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = stats_service.get_feature_details(db, feature_name, days)
        return stats
    except Exception as e:
        logger.error(f"Error getting feature details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
