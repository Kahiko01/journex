"""
Module Model for University Courses
Represents a module within a course (collection of lessons)
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.db.session import Base
import uuid

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    # Module details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_number = Column(Integer, nullable=False, default=0)
    
    # Module settings
    is_published = Column(Boolean, default=True)
    estimated_time_minutes = Column(Integer, default=0)
    
    # Additional metadata - renamed from 'metadata' to avoid SQLAlchemy reserved word
    module_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_number")
    quizzes = relationship("Quiz", back_populates="module", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        # Handle metadata renaming
        if 'metadata' in kwargs:
            kwargs['module_metadata'] = kwargs.pop('metadata')
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Module {self.title}>"
