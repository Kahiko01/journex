"""
Anonymous Data Collection Models
Tracks user behavior without PII (Personally Identifiable Information)
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class AnonymousSession(Base):
    """Anonymous session tracking - no user ID linked"""
    __tablename__ = "anonymous_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Anonymous metadata (no PII)
    country_code = Column(String(10), nullable=True)  # Derived from IP (country only)
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet
    screen_size = Column(String(20), nullable=True)
    
    # Timestamps
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Session stats
    page_views = Column(Integer, default=0)
    time_on_site = Column(Integer, default=0)  # seconds
    interactions = Column(Integer, default=0)

class AnonymousEvent(Base):
    """Anonymous user events - no user ID linked"""
    __tablename__ = "anonymous_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    event_type = Column(String(50), index=True)  # page_view, button_click, feature_use, error
    
    # Event data (aggregatable only, no PII)
    page = Column(String(100), nullable=True)
    component = Column(String(100), nullable=True)
    action = Column(String(100), nullable=True)
    value = Column(String(100), nullable=True)  # anonymized value
    
    # Performance metrics
    load_time = Column(Float, nullable=True)  # ms
    interaction_time = Column(Float, nullable=True)  # ms
    
    # Additional metadata (aggregatable only) - CHANGED FROM 'metadata' TO 'event_data'
    event_data = Column(JSON, nullable=True)  # Store non-PII data (renamed from 'metadata')
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnonymousFeatureUsage(Base):
    """Feature usage statistics - aggregated"""
    __tablename__ = "anonymous_feature_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), index=True)
    date = Column(DateTime(timezone=True), index=True)
    
    # Counts (anonymous)
    use_count = Column(Integer, default=0)
    unique_sessions = Column(Integer, default=0)
    
    # Performance
    avg_interaction_time = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    
    # Satisfaction (if user gives feedback)
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)

class AnonymousError(Base):
    """Anonymous error tracking"""
    __tablename__ = "anonymous_errors"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    error_type = Column(String(100))
    error_message = Column(String(500))  # Generic error message, no stack traces with PII
    page = Column(String(100), nullable=True)
    
    # Context (no PII)
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
