"""
Notification Service for generating and managing notifications
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from collections import defaultdict

from app.models.notification import Notification, NotificationType, NotificationPriority, UserNotificationSettings
from app.models.trade import Trade
from app.models.user import User
from app.schemas.notifications.notification import NotificationCreate

logger = logging.getLogger(__name__)


class NotificationService:
    
    def __init__(self):
        pass
    
    # ==================== CRUD Operations ====================
    
    def create_notification(self, db: Session, notification: NotificationCreate) -> Notification:
        """Create a new notification"""
        db_notification = Notification(
            user_id=notification.user_id,
            type=notification.type,
            priority=notification.priority,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            expires_at=notification.expires_at
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        
        logger.info(f"Notification created for user {notification.user_id}: {notification.type}")
        return db_notification
    
    def get_user_notifications(self, db: Session, user_id: int, 
                              include_read: bool = True, 
                              limit: int = 50) -> List[Notification]:
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if not include_read:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True, "read_at": datetime.utcnow()})
        
        db.commit()
        return result
    
    def delete_notification(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        result = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).delete()
        
        db.commit()
        return result > 0
    
    def get_notification_count(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get notification counts for a user"""
        notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
        
        total = len(notifications)
        unread = len([n for n in notifications if not n.is_read])
        
        # Count by type
        by_type = defaultdict(int)
        for n in notifications:
            by_type[n.type.value] += 1
        
        return {
            "total": total,
            "unread": unread,
            "by_type": dict(by_type)
        }
    
    # ==================== Settings Management ====================
    
    def get_user_settings(self, db: Session, user_id: int) -> UserNotificationSettings:
        """Get or create notification settings for a user"""
        settings = db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = UserNotificationSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings
    
    def update_settings(self, db: Session, user_id: int, 
                       settings_update: Dict[str, Any]) -> UserNotificationSettings:
        """Update notification settings"""
        settings = self.get_user_settings(db, user_id)
        
        for key, value in settings_update.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        db.commit()
        db.refresh(settings)
        return settings
    
    # ==================== Sound & DND Management ====================
    
    def should_play_sound_for_notification(self, db: Session, user_id: int, priority: str) -> bool:
        """Check if sound should play for a notification"""
        settings = self.get_user_settings(db, user_id)
        
        # Check if sound is enabled
        if not settings.sound_enabled:
            return False
        
        # Check DND status
        if settings.dnd_enabled:
            # Only urgent notifications bypass DND
            if priority != NotificationPriority.URGENT.value:
                return False
        
        return True
    
    def should_show_notification(self, db: Session, user_id: int, priority: str) -> bool:
        """Check if notification should be shown (respects DND settings)"""
        settings = self.get_user_settings(db, user_id)
        
        if not settings.dnd_enabled:
            return True
        
        # During DND, only show notifications above the threshold
        priority_levels = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "urgent": 4
        }
        
        notification_level = priority_levels.get(priority, 1)
        threshold_level = priority_levels.get(settings.dnd_priority_threshold.value, 4)
        
        return notification_level >= threshold_level
    
    # ==================== Notification Generators ====================
    
    def check_streaks(self, db: Session, user_id: int) -> List[Notification]:
        """Check for winning/losing streaks and generate alerts"""
        settings = self.get_user_settings(db, user_id)
        if not settings.streak_alerts_enabled:
            return []
        
        # Get recent trades (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time >= thirty_days_ago
        ).order_by(Trade.exit_time.desc()).all()
        
        if len(trades) < settings.streak_threshold:
            return []
        
        # Calculate current streak
        current_streak = 0
        streak_type = None
        notifications = []
        
        for i, trade in enumerate(trades):
            is_win = trade.profit_loss and trade.profit_loss > 0
            
            if i == 0:
                streak_type = "win" if is_win else "loss"
                current_streak = 1
            else:
                prev_trade = trades[i-1]
                prev_win = prev_trade.profit_loss and prev_trade.profit_loss > 0
                
                if (streak_type == "win" and is_win) or (streak_type == "loss" and not is_win):
                    current_streak += 1
                else:
                    break
        
        # Log for debugging
        logger.info(f"User {user_id}: Current streak: {current_streak} {streak_type}, threshold: {settings.streak_threshold}")
        
        # Check if streak meets threshold
        if current_streak >= settings.streak_threshold:
            # Check if we already sent a notification for this streak (in last 24 hours)
            recent = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == NotificationType.STREAK_ALERT,
                Notification.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).first()
            
            if not recent:
                notification = self.create_notification(db, NotificationCreate(
                    user_id=user_id,
                    type=NotificationType.STREAK_ALERT,
                    priority=NotificationPriority.MEDIUM,
                    title=f"🔥 {current_streak}-Trade {streak_type.capitalize()} Streak!",
                    message=f"You're on a {current_streak}-trade {streak_type} streak. Keep it up!",
                    data={"streak": current_streak, "type": streak_type}
                ))
                notifications.append(notification)
                logger.info(f"Created streak notification for user {user_id}")
        
        return notifications
    
    def check_risk_warnings(self, db: Session, user_id: int) -> List[Notification]:
        """Check for risk warnings (drawdown, daily loss, etc.)"""
        settings = self.get_user_settings(db, user_id)
        if not settings.risk_warnings_enabled:
            return []
        
        # Get today's trades
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time >= today_start
        ).all()
        
        # Check daily loss
        if settings.daily_loss_threshold > 0:
            daily_loss = sum(t.profit_loss for t in today_trades if t.profit_loss and t.profit_loss < 0)
            if abs(daily_loss) >= settings.daily_loss_threshold:
                notification = self.create_notification(db, NotificationCreate(
                    user_id=user_id,
                    type=NotificationType.RISK_WARNING,
                    priority=NotificationPriority.HIGH,
                    title="Daily Loss Limit Reached",
                    message=f"You've lost ${abs(daily_loss):.2f} today, which exceeds your limit of ${settings.daily_loss_threshold:.2f}.",
                    data={"loss": abs(daily_loss), "limit": settings.daily_loss_threshold, "period": "daily"}
                ))
                return [notification]
        
        # Check drawdown
        if settings.drawdown_threshold > 0:
            # Calculate current drawdown (simplified)
            trades = db.query(Trade).filter(Trade.user_id == user_id).order_by(Trade.exit_time).all()
            if trades:
                equity = 10000
                peak = equity
                for trade in trades:
                    equity += trade.profit_loss or 0
                    if equity > peak:
                        peak = equity
                
                current_drawdown = (peak - equity) / peak * 100 if peak > 0 else 0
                
                if current_drawdown >= settings.drawdown_threshold:
                    notification = self.create_notification(db, NotificationCreate(
                        user_id=user_id,
                        type=NotificationType.RISK_WARNING,
                        priority=NotificationPriority.HIGH,
                        title="Significant Drawdown Detected",
                        message=f"Your account is down {current_drawdown:.1f}% from its peak. Consider reducing risk.",
                        data={"drawdown": current_drawdown, "threshold": settings.drawdown_threshold}
                    ))
                    return [notification]
        
        return []
    
    def check_goal_achievements(self, db: Session, user_id: int) -> List[Notification]:
        """Check for goal achievements"""
        settings = self.get_user_settings(db, user_id)
        if not settings.goal_alerts_enabled:
            return []
        
        notifications = []
        
        # Get this month's trades
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time >= month_start
        ).all()
        
        month_pl = sum(t.profit_loss or 0 for t in month_trades)
        
        # Check monthly goal
        if settings.monthly_goal and month_pl >= settings.monthly_goal:
            # Check if we already notified
            recent = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == NotificationType.GOAL_ACHIEVEMENT,
                Notification.created_at >= month_start
            ).first()
            
            if not recent:
                notification = self.create_notification(db, NotificationCreate(
                    user_id=user_id,
                    type=NotificationType.GOAL_ACHIEVEMENT,
                    priority=NotificationPriority.HIGH,
                    title="Monthly Profit Goal Achieved! 🎉",
                    message=f"Congratulations! You've reached your monthly profit goal of ${settings.monthly_goal:.2f}.",
                    data={"goal": settings.monthly_goal, "achieved": month_pl, "period": "monthly"}
                ))
                notifications.append(notification)
        
        # Check weekly goal
        if settings.weekly_goal:
            week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_trades = db.query(Trade).filter(
                Trade.user_id == user_id,
                Trade.exit_time >= week_start
            ).all()
            
            week_pl = sum(t.profit_loss or 0 for t in week_trades)
            
            if week_pl >= settings.weekly_goal:
                recent = db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.type == NotificationType.GOAL_ACHIEVEMENT,
                    Notification.created_at >= week_start
                ).first()
                
                if not recent:
                    notification = self.create_notification(db, NotificationCreate(
                        user_id=user_id,
                        type=NotificationType.GOAL_ACHIEVEMENT,
                        priority=NotificationPriority.HIGH,
                        title="Weekly Profit Goal Achieved! 🎯",
                        message=f"Great job! You've hit your weekly profit target of ${settings.weekly_goal:.2f}.",
                        data={"goal": settings.weekly_goal, "achieved": week_pl, "period": "weekly"}
                    ))
                    notifications.append(notification)
        
        return notifications
    
    def check_all_triggers(self, db: Session, user_id: int) -> List[Notification]:
        """Check all notification triggers for a user"""
        notifications = []
        notifications.extend(self.check_streaks(db, user_id))
        notifications.extend(self.check_risk_warnings(db, user_id))
        notifications.extend(self.check_goal_achievements(db, user_id))
        return notifications
    
    def check_all_users(self, db: Session) -> Dict[int, List[Notification]]:
        """Check notification triggers for all active users"""
        users = db.query(User).filter(User.is_active == True).all()
        
        results = {}
        for user in users:
            try:
                notifications = self.check_all_triggers(db, user.id)
                if notifications:
                    results[user.id] = notifications
            except Exception as e:
                logger.error(f"Error checking notifications for user {user.id}: {e}")
        
        return results
