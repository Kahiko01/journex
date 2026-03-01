"""
Trading Plan Models for Rule Definition and Tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TradingPlan(Base):
    """Main trading plan definition"""
    __tablename__ = "trading_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Plan metadata
    tags = Column(JSON, default=list)  # ['trend-following', 'scalping', etc.]
    risk_percentage = Column(Float, default=1.0)  # Default risk per trade
    max_daily_loss = Column(Float, nullable=True)
    max_weekly_loss = Column(Float, nullable=True)
    max_positions = Column(Integer, default=1)

class TradingRule(Base):
    """Individual rules within a trading plan"""
    __tablename__ = "trading_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("trading_plans.id", ondelete="CASCADE"))
    user_id = Column(Integer, nullable=False, index=True)
    
    # Rule definition
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # 'entry', 'exit', 'risk', 'session', 'general'
    
    # Rule conditions (stored as JSON for flexibility)
    conditions = Column(JSON, nullable=False, default=dict)
    # Example:
    # {
    #   "type": "max_risk",
    #   "operator": "<=",
    #   "value": 2.0,
    #   "unit": "percent"
    # }
    
    # Rule severity
    is_required = Column(Boolean, default=True)  # Must follow vs nice to have
    penalty_score = Column(Integer, default=10)  # Points deducted for violation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class RuleViolation(Base):
    """Track when rules are violated"""
    __tablename__ = "rule_violations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("trading_rules.id", ondelete="CASCADE"))
    trade_id = Column(Integer, nullable=True)  # Optional link to specific trade
    
    # Violation details
    violation_date = Column(DateTime, default=datetime.utcnow)
    rule_name = Column(String(200))
    rule_type = Column(String(50))
    description = Column(Text)
    severity = Column(String(20), default='medium')  # 'low', 'medium', 'high'
    
    # Context
    expected_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    trade_data = Column(JSON, nullable=True)  # Snapshot of trade if applicable
    
    # Resolution
    is_reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

class WeeklyReview(Base):
    """Weekly review of plan adherence"""
    __tablename__ = "weekly_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("trading_plans.id", ondelete="CASCADE"))
    
    # Review period
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    
    # Statistics
    total_trades = Column(Integer, default=0)
    violations_count = Column(Integer, default=0)
    adherence_rate = Column(Float, default=0)  # Percentage of rules followed
    discipline_score = Column(Integer, default=0)  # 0-100
    
    # Detailed metrics
    rule_stats = Column(JSON, default=dict)  # Stats per rule
    improvement_notes = Column(Text, nullable=True)
    
    # Generated report
    report_pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create indexes for performance
# These will be created via Alembic migrations
