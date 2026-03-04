"""
Notification Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    STREAK_ALERT = "streak_alert"
    RISK_WARNING = "risk_warning"
    GOAL_ACHIEVEMENT = "goal_achievement"
    TRADE_REMINDER = "trade_reminder"
    SYSTEM_UPDATE = "system_update"
    WEEKLY_REPORT = "weekly_report"
    PERFORMANCE_MILESTONE = "performance_milestone"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationBase(BaseModel):
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    is_archived: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationSettingsBase(BaseModel):
    # Streak alerts
    streak_alerts_enabled: bool = True
    streak_threshold: int = 3
    
    # Risk warnings
    risk_warnings_enabled: bool = True
    daily_loss_threshold: float = 500.0
    weekly_loss_threshold: float = 2000.0
    drawdown_threshold: float = 10.0
    
    # Goal achievements
    goal_alerts_enabled: bool = True
    monthly_goal: Optional[float] = None
    weekly_goal: Optional[float] = None
    
    # Email notifications
    email_notifications: bool = False
    
    # Sound settings
    sound_enabled: bool = True
    sound_volume: int = Field(70, ge=0, le=100)
    sound_type: str = "chime"
    
    # Do Not Disturb settings
    dnd_enabled: bool = False
    dnd_start: str = "22:00"
    dnd_end: str = "08:00"
    dnd_priority_threshold: NotificationPriority = NotificationPriority.URGENT

class NotificationSettingsUpdate(BaseModel):
    # Streak alerts
    streak_alerts_enabled: Optional[bool] = None
    streak_threshold: Optional[int] = None
    
    # Risk warnings
    risk_warnings_enabled: Optional[bool] = None
    daily_loss_threshold: Optional[float] = None
    weekly_loss_threshold: Optional[float] = None
    drawdown_threshold: Optional[float] = None
    
    # Goal achievements
    goal_alerts_enabled: Optional[bool] = None
    monthly_goal: Optional[float] = None
    weekly_goal: Optional[float] = None
    
    # Email notifications
    email_notifications: Optional[bool] = None
    
    # Sound settings
    sound_enabled: Optional[bool] = None
    sound_volume: Optional[int] = Field(None, ge=0, le=100)
    sound_type: Optional[str] = None
    
    # Do Not Disturb settings
    dnd_enabled: Optional[bool] = None
    dnd_start: Optional[str] = None
    dnd_end: Optional[str] = None
    dnd_priority_threshold: Optional[NotificationPriority] = None

class NotificationSettingsResponse(NotificationSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationCountResponse(BaseModel):
    total: int
    unread: int
    by_type: Dict[str, int]
