"""
Anonymous Tracking Service
Collects anonymized user data for analytics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from user_agents import parse
import geoip2.database
import uuid

from app.models.anonymous_data import (
    AnonymousSession, AnonymousEvent, 
    AnonymousFeatureUsage, AnonymousError
)

logger = logging.getLogger(__name__)


class AnonymousTrackingService:
    def __init__(self):
        # Initialize GeoIP database (you'll need to download this)
        # self.geoip_reader = geoip2.database.Reader('/path/to/GeoLite2-Country.mmdb')
        pass
    
    def get_or_create_session(self, db: Session, session_id: Optional[str] = None, 
                              headers: Optional[Dict] = None) -> str:
        """Get existing session or create new anonymous session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = db.query(AnonymousSession).filter(
            AnonymousSession.session_id == session_id
        ).first()
        
        if not session:
            # Parse user agent for anonymous data
            user_agent = headers.get('user-agent', '') if headers else ''
            ua = parse(user_agent)
            
            session = AnonymousSession(
                session_id=session_id,
                browser=ua.browser.family if ua.browser.family else 'Unknown',
                os=ua.os.family if ua.os.family else 'Unknown',
                device_type=self._get_device_type(ua),
                page_views=1  # Start with 1 for current page
            )
            db.add(session)
            db.commit()
            logger.info(f"New anonymous session created: {session_id}")
        else:
            # Update last seen and page views
            session.last_seen = datetime.utcnow()
            session.page_views += 1
            db.commit()
        
        return session_id
    
    def track_event(self, db: Session, session_id: str, event_type: str, 
                   page: Optional[str] = None, component: Optional[str] = None,
                   action: Optional[str] = None, value: Optional[str] = None,
                   load_time: Optional[float] = None, metadata: Optional[Dict] = None):
        """Track an anonymous event"""
        try:
            event = AnonymousEvent(
                session_id=session_id,
                event_type=event_type,
                page=page,
                component=component,
                action=action,
                value=value,
                load_time=load_time,
                event_data=metadata  # ✅ Changed from 'metadata' to 'event_data'
            )
            db.add(event)
            
            # Update session interaction count
            session = db.query(AnonymousSession).filter(
                AnonymousSession.session_id == session_id
            ).first()
            if session:
                session.interactions += 1
            
            db.commit()
            logger.info(f"Event tracked: {event_type} for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            db.rollback()
    
    def track_error(self, db: Session, session_id: str, error_type: str,
                   error_message: str, page: Optional[str] = None,
                   headers: Optional[Dict] = None):
        """Track an anonymous error"""
        try:
            user_agent = headers.get('user-agent', '') if headers else ''
            ua = parse(user_agent)
            
            error = AnonymousError(
                session_id=session_id,
                error_type=error_type,
                error_message=error_message[:500],  # Truncate
                page=page,
                browser=ua.browser.family if ua.browser.family else 'Unknown',
                os=ua.os.family if ua.os.family else 'Unknown'
            )
            db.add(error)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking error: {e}")
            db.rollback()
    
    def track_feature_usage(self, db: Session, feature_name: str, 
                           session_id: str, interaction_time: Optional[float] = None):
        """Track usage of a specific feature"""
        try:
            today = date.today()
            usage = db.query(AnonymousFeatureUsage).filter(
                AnonymousFeatureUsage.feature_name == feature_name,
                AnonymousFeatureUsage.date >= today,
                AnonymousFeatureUsage.date < today.replace(day=today.day+1)
            ).first()
            
            if not usage:
                usage = AnonymousFeatureUsage(
                    feature_name=feature_name,
                    date=datetime.utcnow(),
                    use_count=1,
                    unique_sessions=1
                )
                db.add(usage)
            else:
                usage.use_count += 1
                
                # Check if this is a new session for this feature today
                # This is simplified - you'd want to track unique sessions per feature
                usage.unique_sessions += 1
            
            if interaction_time:
                # Update rolling average
                if usage.avg_interaction_time:
                    total_time = usage.avg_interaction_time * (usage.use_count - 1) + interaction_time
                    usage.avg_interaction_time = total_time / usage.use_count
                else:
                    usage.avg_interaction_time = interaction_time
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking feature usage: {e}")
            db.rollback()
    
    def track_feedback(self, db: Session, feature_name: str, positive: bool):
        """Track user feedback on features (anonymous)"""
        try:
            today = date.today()
            usage = db.query(AnonymousFeatureUsage).filter(
                AnonymousFeatureUsage.feature_name == feature_name,
                AnonymousFeatureUsage.date >= today,
                AnonymousFeatureUsage.date < today.replace(day=today.day+1)
            ).first()
            
            if not usage:
                usage = AnonymousFeatureUsage(
                    feature_name=feature_name,
                    date=datetime.utcnow()
                )
                db.add(usage)
            
            if positive:
                usage.positive_feedback += 1
            else:
                usage.negative_feedback += 1
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking feedback: {e}")
            db.rollback()
    
    def get_anonymous_stats(self, db: Session, days: int = 30) -> Dict:
        """Get anonymous aggregated statistics"""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Total unique sessions
        total_sessions = db.query(AnonymousSession).filter(
            AnonymousSession.first_seen >= cutoff
        ).count()
        
        # Total events
        total_events = db.query(AnonymousEvent).filter(
            AnonymousEvent.created_at >= cutoff
        ).count()
        
        # Top pages
        top_pages = db.query(
            AnonymousEvent.page, 
            db.func.count().label('count')
        ).filter(
            AnonymousEvent.created_at >= cutoff,
            AnonymousEvent.page.isnot(None)
        ).group_by(AnonymousEvent.page).order_by(db.desc('count')).limit(10).all()
        
        # Top features
        top_features = db.query(
            AnonymousFeatureUsage.feature_name,
            db.func.sum(AnonymousFeatureUsage.use_count).label('total_uses')
        ).filter(
            AnonymousFeatureUsage.date >= cutoff
        ).group_by(AnonymousFeatureUsage.feature_name).order_by(
            db.desc('total_uses')
        ).limit(10).all()
        
        # Error rates
        total_errors = db.query(AnonymousError).filter(
            AnonymousError.created_at >= cutoff
        ).count()
        
        # Device breakdown
        devices = db.query(
            AnonymousSession.device_type,
            db.func.count().label('count')
        ).filter(
            AnonymousSession.first_seen >= cutoff
        ).group_by(AnonymousSession.device_type).all()
        
        return {
            "total_sessions": total_sessions,
            "total_events": total_events,
            "total_errors": total_errors,
            "error_rate": round(total_errors / total_events * 100, 2) if total_events > 0 else 0,
            "top_pages": [{"page": p[0], "views": p[1]} for p in top_pages],
            "top_features": [{"feature": f[0], "uses": f[1]} for f in top_features],
            "device_breakdown": [{"device": d[0], "sessions": d[1]} for d in devices]
        }
    
    def _get_country_from_ip(self, ip: str) -> Optional[str]:
        """Get country from IP address (anonymized)"""
        try:
            # This would use geoip2 database
            # response = self.geoip_reader.country(ip)
            # return response.country.iso_code
            return None  # Placeholder - implement with actual GeoIP
        except:
            return None
    
    def _get_device_type(self, ua) -> str:
        """Determine device type from user agent"""
        if ua.is_mobile:
            return "mobile"
        elif ua.is_tablet:
            return "tablet"
        elif ua.is_pc:
            return "desktop"
        else:
            return "other"
    
    def _update_feature_usage(self, db: Session, event_type: str, 
                             page: Optional[str], component: Optional[str],
                             action: Optional[str]):
        """Update feature usage stats based on event"""
        if event_type == 'feature_use' and component:
            feature_name = f"{page}.{component}" if page else component
            if action:
                feature_name = f"{feature_name}.{action}"
            
            # This is simplified - you'd want to aggregate properly
            # self.track_feature_usage(db, feature_name, session_id)
            pass
