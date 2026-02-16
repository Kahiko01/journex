from sqlalchemy import Column, String, Text, Integer, Boolean, Float, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class CertificationLevel(Base):
    __tablename__ = "certification_levels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)  # Bronze, Silver, Gold, Elite
    level_order = Column(Integer, nullable=False)  # 1,2,3,4
    
    requirements = Column(JSON, nullable=False, default={
        "min_discipline_score": 0,
        "min_risk_consistency": 0,
        "min_avg_r_multiple": 0,
        "max_drawdown_percent": 100,
        "min_quiz_score": 0,
        "max_rule_violations": 999,
        "min_trades_analyzed": 0,
        "consecutive_weeks_required": 0
    })
    
    badge_color = Column(String(50))
    badge_icon = Column(String(255))
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_number = Column(String(100), unique=True, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    certification_level_id = Column(UUID(as_uuid=True), ForeignKey("certification_levels.id"))
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id"), nullable=True)
    
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Metrics at time of issuance
    final_discipline_score = Column(Float)
    final_risk_consistency = Column(Float)
    final_avg_r_multiple = Column(Float)
    final_quiz_average = Column(Float)
    trades_analyzed = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoke_reason = Column(String(500), nullable=True)
    
    # PDF
    pdf_url = Column(String(500))
    public_verification_url = Column(String(500), unique=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    INDEX idx_certificates_user (user_id),
    INDEX idx_certificates_number (certificate_number),
    INDEX idx_certificates_active (is_active)


class CertificationEligibilityLog(Base):
    __tablename__ = "certification_eligibility_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    certification_level_id = Column(UUID(as_uuid=True), ForeignKey("certification_levels.id"))
    
    checked_at = Column(DateTime, default=datetime.utcnow)
    is_eligible = Column(Boolean)
    
    requirements_met = Column(JSON)
    requirements_missing = Column(JSON)
    
    calculated_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
