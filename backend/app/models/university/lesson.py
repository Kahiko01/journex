"""
Lesson Model for University Courses
Represents a lesson within a module
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.db.session import Base
import uuid

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(String(36), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    
    # Lesson details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Markdown/HTML content
    video_url = Column(String(500), nullable=True)
    order_number = Column(Integer, nullable=False, default=0)
    
    # Lesson settings
    is_published = Column(Boolean, default=True)
    duration_minutes = Column(Integer, default=0)
    
    # Resources
    resources = Column(JSON, nullable=True)  # Additional resources (PDFs, links)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    
    def __repr__(self):
        return f"<Lesson {self.title}>"
