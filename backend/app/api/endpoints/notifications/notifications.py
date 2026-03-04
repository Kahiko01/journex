"""
Notification API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.services.notifications.notification_service import NotificationService
from app.schemas.notifications.notification import (
    NotificationResponse, NotificationUpdate, NotificationCountResponse,
    NotificationSettingsResponse, NotificationSettingsUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()

# ==================== Notification Endpoints ====================

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    include_read: bool = Query(False, description="Include read notifications"),
    limit: int = Query(50, description="Number of notifications to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        notifications = notification_service.get_user_notifications(
            db, current_user.id, include_read, limit
        )
        return notifications
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/count", response_model=NotificationCountResponse)
async def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification counts for the current user"""
    try:
        counts = notification_service.get_notification_count(db, current_user.id)
        return counts
    except Exception as e:
        logger.error(f"Error getting notification count: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        notification = notification_service.mark_as_read(db, notification_id, current_user.id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    try:
        count = notification_service.mark_all_as_read(db, current_user.id)
        return {"message": f"Marked {count} notifications as read"}
    except Exception as e:
        logger.error(f"Error marking all as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        success = notification_service.delete_notification(db, notification_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Settings Endpoints ====================

@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification settings for the current user"""
    try:
        settings = notification_service.get_user_settings(db, current_user.id)
        return settings
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification settings"""
    try:
        settings = notification_service.update_settings(
            db, current_user.id, settings_update.model_dump(exclude_unset=True)
        )
        return settings
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Manual Trigger (for testing) ====================

@router.post("/check")
async def check_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger notification checks (for testing)"""
    try:
        notifications = notification_service.check_all_triggers(db, current_user.id)
        return {
            "message": f"Generated {len(notifications)} new notifications",
            "notifications": notifications
        }
    except Exception as e:
        logger.error(f"Error checking notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Admin Endpoint ====================

@router.post("/check-all-users")
async def check_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check notifications for all users (admin only)"""
    # Simple admin check - you can enhance this
    if current_user.username not in ["testuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        results = notification_service.check_all_users(db)
        total = sum(len(notifs) for notifs in results.values())
        return {
            "message": f"Generated {total} notifications across {len(results)} users",
            "details": {str(uid): len(notifs) for uid, notifs in results.items()}
        }
    except Exception as e:
        logger.error(f"Error checking all users: {e}")
        raise HTTPException(status_code=500, detail=str(e))
