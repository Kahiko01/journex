from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, DateTime, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class DisciplineScore(Base):
    __tablename__ = "discipline_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=True)
    
    # Score components (each 0-100)
    risk_adherence = Column(Float, default=0)        # Using stop losses, proper position sizing
    rule_compliance = Column(Float, default=0)       # Following trading plan rules
    overtrading_control = Column(Float, default=0)   # Not exceeding daily trade limits
    strategy_adherence = Column(Float, default=0)    # Sticking to defined strategies
    drawdown_management = Column(Float, default=0)   # Controlling losses
    emotional_control = Column(Float, default=0)     # Emotion tagging consistency
    
    # Weighted total (using formula: 0.25*risk + 0.20*rule + 0.15*overtrading + 0.15*strategy + 0.15*drawdown + 0.10*emotional)
    total_score = Column(Float, default=0)
    
    # Weekly tracking
    week_number = Column(Integer)
    year = Column(Integer)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    
    # Metrics snapshot
    metrics_snapshot = Column(JSON)  # Stores raw metrics used for calculation
    
    __table_args__ = (
        UniqueConstraint('user_id', 'cohort_id', 'week_number', 'year', name='unique_weekly_discipline'),
        Index('idx_discipline_user_week', 'user_id', 'year', 'week_number'),
        Index('idx_discipline_score', 'total_score')
    )


class GraduationRecord(Base):
    __tablename__ = "graduation_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"))
    
    graduated_at = Column(DateTime, default=datetime.utcnow)
    
    # Final metrics
    final_discipline_score = Column(Float)
    final_risk_consistency = Column(Float)
    final_quiz_average = Column(Float)
    lessons_completed = Column(Integer)
    attendance_rate = Column(Float)
    
    # Honors
    honors_level = Column(String(50))  # summa cum laude, magna cum laude, cum laude, pass
    
    # Certificate
    certificate_id = Column(String(100), unique=True)
    certificate_url = Column(String(500))
    
    # Requirements check
    requirements_met = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    INDEX idx_graduation_user (user_id),
    INDEX idx_graduation_cohort (cohort_id)
