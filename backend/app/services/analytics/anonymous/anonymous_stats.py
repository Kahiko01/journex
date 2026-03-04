"""
Anonymous Statistics Service
Provides aggregated anonymous data for the admin dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from app.models.anonymous_data import (
    AnonymousSession, AnonymousEvent, 
    AnonymousFeatureUsage, AnonymousError
)

logger = logging.getLogger(__name__)

class AnonymousStatsService:
    
    def get_dashboard_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get all anonymous statistics for the dashboard"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Basic stats
        total_sessions = db.query(AnonymousSession).filter(
            AnonymousSession.first_seen >= cutoff
        ).count()
        
        total_events = db.query(AnonymousEvent).filter(
            AnonymousEvent.created_at >= cutoff
        ).count()
        
        total_errors = db.query(AnonymousError).filter(
            AnonymousError.created_at >= cutoff
        ).count()
        
        # Active users today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_today = db.query(AnonymousSession).filter(
            AnonymousSession.last_seen >= today_start
        ).count()
        
        # Average session duration
        avg_duration = db.query(
            func.avg(AnonymousSession.time_on_site)
        ).filter(
            AnonymousSession.first_seen >= cutoff
        ).scalar() or 0
        
        # Device breakdown
        devices = db.query(
            AnonymousSession.device_type,
            func.count().label('count')
        ).filter(
            AnonymousSession.first_seen >= cutoff
        ).group_by(AnonymousSession.device_type).all()
        
        # Browser breakdown
        browsers = db.query(
            AnonymousSession.browser,
            func.count().label('count')
        ).filter(
            AnonymousSession.first_seen >= cutoff
        ).group_by(AnonymousSession.browser).order_by(desc('count')).limit(5).all()
        
        # Top pages
        top_pages = db.query(
            AnonymousEvent.page,
            func.count().label('views')
        ).filter(
            AnonymousEvent.created_at >= cutoff,
            AnonymousEvent.event_type == 'page_view'
        ).group_by(AnonymousEvent.page).order_by(desc('views')).limit(10).all()
        
        # Top features
        top_features = db.query(
            AnonymousFeatureUsage.feature_name,
            func.sum(AnonymousFeatureUsage.use_count).label('total_uses')
        ).filter(
            AnonymousFeatureUsage.date >= cutoff
        ).group_by(AnonymousFeatureUsage.feature_name).order_by(
            desc('total_uses')
        ).limit(10).all()
        
        # Feature feedback
        feature_feedback = db.query(
            AnonymousFeatureUsage.feature_name,
            func.sum(AnonymousFeatureUsage.positive_feedback).label('positive'),
            func.sum(AnonymousFeatureUsage.negative_feedback).label('negative')
        ).filter(
            AnonymousFeatureUsage.date >= cutoff
        ).group_by(AnonymousFeatureUsage.feature_name).having(
            (func.sum(AnonymousFeatureUsage.positive_feedback) > 0) | 
            (func.sum(AnonymousFeatureUsage.negative_feedback) > 0)
        ).all()
        
        # Error types
        error_types = db.query(
            AnonymousError.error_type,
            func.count().label('count')
        ).filter(
            AnonymousError.created_at >= cutoff
        ).group_by(AnonymousError.error_type).order_by(desc('count')).limit(5).all()
        
        # Daily activity for chart
        daily_activity = []
        for i in range(days):
            day = cutoff + timedelta(days=i)
            next_day = day + timedelta(days=1)
            
            sessions = db.query(AnonymousSession).filter(
                AnonymousSession.first_seen >= day,
                AnonymousSession.first_seen < next_day
            ).count()
            
            events = db.query(AnonymousEvent).filter(
                AnonymousEvent.created_at >= day,
                AnonymousEvent.created_at < next_day
            ).count()
            
            daily_activity.append({
                'date': day.strftime('%Y-%m-%d'),
                'sessions': sessions,
                'events': events
            })
        
        return {
            'overview': {
                'total_sessions': total_sessions,
                'total_events': total_events,
                'total_errors': total_errors,
                'active_today': active_today,
                'avg_session_duration': round(avg_duration, 2),
                'error_rate': round(total_errors / total_events * 100, 2) if total_events > 0 else 0
            },
            'devices': [{'type': d[0] or 'unknown', 'count': d[1]} for d in devices],
            'browsers': [{'name': b[0] or 'unknown', 'count': b[1]} for b in browsers],
            'top_pages': [{'page': p[0] or 'unknown', 'views': p[1]} for p in top_pages],
            'top_features': [{'feature': f[0], 'uses': f[1]} for f in top_features],
            'feature_feedback': [
                {
                    'feature': f[0],
                    'positive': f[1] or 0,
                    'negative': f[2] or 0,
                    'score': round((f[1] or 0) / ((f[1] or 0) + (f[2] or 0)) * 100, 2) 
                    if (f[1] or 0) + (f[2] or 0) > 0 else 0
                } for f in feature_feedback
            ],
            'error_types': [{'type': e[0], 'count': e[1]} for e in error_types],
            'daily_activity': daily_activity
        }
    
    def get_realtime_stats(self, db: Session) -> Dict[str, Any]:
        """Get real-time anonymous statistics"""
        last_hour = datetime.utcnow() - timedelta(hours=1)
        last_5min = datetime.utcnow() - timedelta(minutes=5)
        
        # Active in last 5 minutes
        active_now = db.query(AnonymousSession).filter(
            AnonymousSession.last_seen >= last_5min
        ).count()
        
        # Events in last hour
        events_last_hour = db.query(AnonymousEvent).filter(
            AnonymousEvent.created_at >= last_hour
        ).count()
        
        # Current page views
        current_pages = db.query(
            AnonymousEvent.page,
            func.count().label('views')
        ).filter(
            AnonymousEvent.created_at >= last_5min,
            AnonymousEvent.event_type == 'page_view'
        ).group_by(AnonymousEvent.page).order_by(desc('views')).limit(5).all()
        
        return {
            'active_users_now': active_now,
            'events_last_hour': events_last_hour,
            'current_pages': [{'page': p[0], 'views': p[1]} for p in current_pages]
        }
    
    def get_feature_details(self, db: Session, feature_name: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed stats for a specific feature"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        usage = db.query(AnonymousFeatureUsage).filter(
            AnonymousFeatureUsage.feature_name == feature_name,
            AnonymousFeatureUsage.date >= cutoff
        ).all()
        
        daily_usage = []
        total_uses = 0
        total_sessions = 0
        
        for u in usage:
            daily_usage.append({
                'date': u.date.strftime('%Y-%m-%d'),
                'uses': u.use_count,
                'sessions': u.unique_sessions
            })
            total_uses += u.use_count
            total_sessions += u.unique_sessions
        
        return {
            'feature_name': feature_name,
            'total_uses': total_uses,
            'unique_sessions': total_sessions,
            'daily_usage': daily_usage
        }
