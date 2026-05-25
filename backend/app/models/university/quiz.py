"""
Quiz Model for University Courses
Represents a quiz within a module
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.db.session import Base
import uuid

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(String(36), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    
    # Quiz details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_number = Column(Integer, nullable=False, default=0)
    
    # Quiz settings
    is_published = Column(Boolean, default=True)
    time_limit_minutes = Column(Integer, nullable=True)
    passing_score = Column(Integer, default=70)  # Percentage required to pass
    
    # Questions (stored as JSON)
    questions = Column(JSON, nullable=False, default=list)
    
    # Statistics
    attempts_count = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="quizzes")
    
    def __repr__(self):
        return f"<Quiz {self.title}>"
