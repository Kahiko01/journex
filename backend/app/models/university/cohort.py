"""
Cohort System Models for Journex University
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

# Association table for cohort members
cohort_members = Table(
    'cohort_members',
    Base.metadata,
    Column('cohort_id', String(36), ForeignKey('cohorts.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Column('completed', Boolean, default=False),
    Column('completed_at', DateTime(timezone=True), nullable=True)
)

class Cohort(Base):
    __tablename__ = "cohorts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Cohort settings
    max_members = Column(Integer, default=50)
    is_private = Column(Boolean, default=False)
    invite_code = Column(String(50), unique=True, nullable=True)
    
    # Leaderboard settings
    leaderboard_enabled = Column(Boolean, default=True)
    show_progress = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("User", secondary=cohort_members, backref="cohorts")
    courses = relationship("CohortCourse", back_populates="cohort", cascade="all, delete-orphan")
    leaderboard = relationship("CohortLeaderboard", back_populates="cohort", uselist=False)

class CohortCourse(Base):
    __tablename__ = "cohort_courses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cohort_id = Column(String(36), ForeignKey("cohorts.id"))
    course_id = Column(String(36), ForeignKey("courses.id"))
    
    # Course-specific settings
    required = Column(Boolean, default=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    cohort = relationship("Cohort", back_populates="courses")
    course = relationship("Course")

class CohortLeaderboard(Base):
    __tablename__ = "cohort_leaderboard"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cohort_id = Column(String(36), ForeignKey("cohorts.id"), unique=True)
    
    # Rankings (stored as JSON for performance)
    rankings = Column(JSON, default=list)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    cohort = relationship("Cohort", back_populates="leaderboard")
    
    def update_rankings(self, db):
        """Calculate and update rankings based on member progress"""
        from app.models.university import UserProgress
        
        rankings = []
        for member in self.cohort.members:
            # Get user's progress across all cohort courses
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == member.id,
                UserProgress.course_id.in_([c.course_id for c in self.cohort.courses])
            ).all()
            
            completed = len([p for p in progress if p.completed])
            total = len(self.cohort.courses)
            percentage = (completed / total * 100) if total > 0 else 0
            
            rankings.append({
                "user_id": member.id,
                "username": member.username,
                "completed": completed,
                "total": total,
                "percentage": round(percentage, 1),
                "avatar_url": member.avatar_url
            })
        
        # Sort by percentage (highest first)
        rankings.sort(key=lambda x: x["percentage"], reverse=True)
        self.rankings = rankings
        self.last_updated = datetime.utcnow()
        db.commit()
