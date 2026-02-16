from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RuleViolation(Base):
    __tablename__ = 'rule_violations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    trade_id = Column(Integer, nullable=True)
    violation_date = Column(DateTime, nullable=False)
    
    # Violation types
    violation_type = Column(String(50), nullable=False)  # 'risk', 'overtrading', 'revenge', 'session', 'strategy'
    severity = Column(String(20), default='medium')  # 'low', 'medium', 'high'
    
    # Details
    description = Column(String(500))
    rule_name = Column(String(100))
    expected_value = Column(Float)
    actual_value = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_user_violation_date', 'user_id', 'violation_date'),
    )

class RuleViolationResponse(BaseModel):
    id: int
    violation_type: str
    severity: str
    description: str
    rule_name: Optional[str]
    violation_date: datetime
    
    class Config:
        from_attributes = True
