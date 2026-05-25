"""
Test endpoints for notifications
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.services.notifications.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test-notifications", tags=["test-notifications"])
notification_service = NotificationService()

@router.post("/trigger-streak")
async def trigger_streak_test(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger streak check for testing"""
    try:
        notifications = notification_service.check_streaks(db, current_user.id)
        return {
            "message": f"Triggered streak check",
            "notifications_created": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error triggering streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-risk")
async def trigger_risk_test(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger risk check for testing"""
    try:
        notifications = notification_service.check_risk_warnings(db, current_user.id)
        return {
            "message": f"Triggered risk check",
            "notifications_created": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error triggering risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-goals")
async def trigger_goals_test(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger goal check for testing"""
    try:
        notifications = notification_service.check_goal_achievements(db, current_user.id)
        return {
            "message": f"Triggered goal check",
            "notifications_created": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error triggering goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))
