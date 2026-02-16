from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DailySummary(Base):
    __tablename__ = 'daily_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    trade_date = Column(DateTime, nullable=False)
    
    # Core metrics
    total_pl = Column(Float, default=0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0)
    
    # Risk metrics
    total_risk_taken = Column(Float, default=0)
    avg_r_multiple = Column(Float, default=0)
    sum_r_multiple = Column(Float, default=0)
    largest_win = Column(Float, default=0)
    largest_loss = Column(Float, default=0)
    avg_rr = Column(Float, default=0)
    
    # Discipline metrics
    discipline_score = Column(Integer, default=0)  # 0-100
    rule_violations_count = Column(Integer, default=0)
    overtrading_detected = Column(Boolean, default=False)
    revenge_trading_detected = Column(Boolean, default=False)
    max_drawdown_spike = Column(Boolean, default=False)
    
    # Session breakdown
    asia_trades = Column(Integer, default=0)
    asia_pl = Column(Float, default=0)
    london_trades = Column(Integer, default=0)
    london_pl = Column(Float, default=0)
    ny_trades = Column(Integer, default=0)
    ny_pl = Column(Float, default=0)
    
    # Strategy performance
    strategy_performance = Column(JSON, default={})
    
    # Emotion tracking
    emotions = Column(JSON, default={})
    
    # High-rated trades
    high_rated_trades = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_user_date', 'user_id', 'trade_date'),
        Index('ix_date', 'trade_date'),
    )

class DailySummaryResponse(BaseModel):
    date: str
    total_pl: float
    total_trades: int
    win_rate: float
    sum_r_multiple: float
    total_risk_taken: float
    largest_win: float
    largest_loss: float
    avg_rr: float
    discipline_score: int
    rule_violations: bool
    overtrading: bool
    revenge_trading: bool
    max_drawdown: bool
    session_breakdown: Dict
    strategy_summary: Dict
    emotions: Dict
    high_rated_count: int
    
    class Config:
        from_attributes = True
