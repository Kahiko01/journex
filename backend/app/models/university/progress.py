"""
User Progress Tracking Model
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    
    # Progress metrics
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Time tracking
    time_spent_minutes = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Module progress (stores which modules are completed)
    modules_completed = Column(JSON, default=list)
    
    # Quiz scores
    quiz_scores = Column(JSON, default=dict)
    average_score = Column(Float, default=0.0)
    
    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_id = Column(String(100), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    course = relationship("Course")
