from sqlalchemy import Column, String, Text, Integer, Boolean, Float, ForeignKey, DateTime, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Cohort(Base):
    __tablename__ = "cohorts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_weeks = Column(Integer)
    
    max_students = Column(Integer, default=50)
    current_students = Column(Integer, default=0)
    
    status = Column(String(50), default="upcoming")
    is_private = Column(Boolean, default=False)
    invite_code = Column(String(50), unique=True)
    
    requirements = Column(JSON, default={
        "min_discipline_score": 70,
        "min_risk_consistency": 65,
        "max_allowed_violations": 5,
        "min_lessons_completed": 80,
        "min_quiz_score": 70
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CohortMember(Base):
    __tablename__ = "cohort_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    role = Column(String(50), default="student")
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    lessons_completed = Column(Integer, default=0)
    lessons_percentage = Column(Float, default=0)
    average_quiz_score = Column(Float, default=0)
    
    discipline_score = Column(Float, default=0)
    risk_consistency = Column(Float, default=0)
    rule_compliance = Column(Float, default=0)
    
    total_points = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    dropped_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('cohort_id', 'user_id', name='unique_cohort_member'),
    )


class CohortMilestone(Base):
    __tablename__ = "cohort_milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"))
    week_number = Column(Integer, nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    required_lessons = Column(Integer, default=0)
    required_quiz_score = Column(Integer, default=70)
    required_discipline_score = Column(Integer, default=65)
    required_trades = Column(Integer, default=0)
    max_allowed_violations = Column(Integer, default=2)
    
    reward_points = Column(Integer, default=100)
    bonus_points = Column(Integer, default=50)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('cohort_id', 'week_number', name='unique_cohort_week'),
    )


class MilestoneCompletion(Base):
    __tablename__ = "milestone_completions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("cohort_milestones.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    completed_at = Column(DateTime, default=datetime.utcnow)
    achieved_points = Column(Integer, default=0)
    earned_bonus = Column(Boolean, default=False)
    
    metrics_snapshot = Column(JSON)
    
    __table_args__ = (
        UniqueConstraint('milestone_id', 'user_id', name='unique_milestone_user'),
    )


class CohortWeeklySnapshot(Base):
    __tablename__ = "cohort_weekly_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="CASCADE"))
    week_number = Column(Integer, nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    
    total_active_students = Column(Integer, default=0)
    avg_discipline_score = Column(Float, default=0)
    avg_risk_consistency = Column(Float, default=0)
    avg_lessons_completed = Column(Float, default=0)
    dropout_count = Column(Integer, default=0)
    
    top_performers = Column(JSON)
    at_risk_students = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
