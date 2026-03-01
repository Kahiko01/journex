"""
Checklist Models for Trading Preparation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class ChecklistTemplate(Base):
    """Predefined checklist templates"""
    __tablename__ = "checklist_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(String(50))  # 'pre-trade', 'post-trade', 'daily', 'weekly'
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Template items stored as JSON for flexibility
    items = Column(JSON, nullable=False, default=list)  # List of {text: "", required: true/false, order: 1}

class UserChecklist(Base):
    """User-specific checklist instances"""
    __tablename__ = "user_checklists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    checklist_type = Column(String(50))  # 'pre-trade', 'post-trade', 'daily', 'weekly'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Custom items
    items = Column(JSON, nullable=False, default=list)  # List of {id: uuid, text: "", required: true, order: 1}

class ChecklistCompletion(Base):
    """Track checklist completions for trades"""
    __tablename__ = "checklist_completions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    checklist_id = Column(UUID(as_uuid=True), nullable=False)
    trade_id = Column(Integer, nullable=True)  # Optional link to a trade
    completed_at = Column(DateTime, default=datetime.utcnow)
    completion_data = Column(JSON, nullable=False, default=dict)  # {item_id: true/false, notes: ""}
    
    # Metrics
    completion_percentage = Column(Float, default=0)
    time_spent_seconds = Column(Integer, default=0)

class ChecklistAnalytics(Base):
    """Analytics for checklist adherence"""
    __tablename__ = "checklist_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    checklist_type = Column(String(50))
    
    # Stats
    total_checks = Column(Integer, default=0)
    completed_checks = Column(Integer, default=0)
    adherence_rate = Column(Float, default=0)
    trades_with_checklist = Column(Integer, default=0)
    
    # Store detailed metrics
    metrics = Column(JSON, default=dict)
