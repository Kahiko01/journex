"""
Notification Models for in-app alerts
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class NotificationType(enum.Enum):
    STREAK_ALERT = "streak_alert"
    RISK_WARNING = "risk_warning"
    GOAL_ACHIEVEMENT = "goal_achievement"
    TRADE_REMINDER = "trade_reminder"
    SYSTEM_UPDATE = "system_update"
    WEEKLY_REPORT = "weekly_report"
    PERFORMANCE_MILESTONE = "performance_milestone"

class NotificationPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # Notification content
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    data = Column(JSON, nullable=True)  # Additional data (e.g., streak count, risk percentage)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="notifications")

class UserNotificationSettings(Base):
    __tablename__ = "user_notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # Streak alerts
    streak_alerts_enabled = Column(Boolean, default=True)
    streak_threshold = Column(Integer, default=3)  # Alert after X consecutive wins/losses
    
    # Risk warnings
    risk_warnings_enabled = Column(Boolean, default=True)
    daily_loss_threshold = Column(Float, default=500.0)  # Alert when daily loss exceeds this
    weekly_loss_threshold = Column(Float, default=2000.0)
    drawdown_threshold = Column(Float, default=10.0)  # Alert when drawdown exceeds X%
    
    # Goal achievements
    goal_alerts_enabled = Column(Boolean, default=True)
    monthly_goal = Column(Float, nullable=True)  # Monthly profit target
    weekly_goal = Column(Float, nullable=True)   # Weekly profit target
    
    # Email notifications (in addition to in-app)
    email_notifications = Column(Boolean, default=False)
    
    # Sound settings
    sound_enabled = Column(Boolean, default=True)
    sound_volume = Column(Integer, default=70)  # 0-100
    sound_type = Column(String(20), default="chime")  # chime, bell, alert, none
    
    # Do Not Disturb settings
    dnd_enabled = Column(Boolean, default=False)
    dnd_start = Column(String(5), default="22:00")  # Format: "HH:MM"
    dnd_end = Column(String(5), default="08:00")    # Format: "HH:MM"
    dnd_priority_threshold = Column(Enum(NotificationPriority), default=NotificationPriority.URGENT)  # Only show urgent during DND
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="notification_settings")
