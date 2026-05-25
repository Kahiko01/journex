"""
Course Model for Journex University
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Course metadata
    category = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced
    duration_minutes = Column(Integer, default=0)
    
    # Course media
    image_url = Column(String(500), nullable=True)
    
    # PDF attachment
    pdf_filename = Column(String(255), nullable=True)
    
    # Course status
    status = Column(String(50), default="published")  # draft, published, archived
    
    # Additional data
    learning_objectives = Column(JSON, nullable=True)  # List of learning objectives
    prerequisites = Column(JSON, nullable=True)  # List of prerequisites
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order_number")
    
    def __init__(self, **kwargs):
        if 'title' in kwargs and 'slug' not in kwargs:
            # Generate slug from title
            self.slug = self.generate_slug(kwargs['title'])
        super().__init__(**kwargs)
    
    def generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from title"""
        import re
        slug = title.lower()
        # Replace spaces and special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def __repr__(self):
        return f"<Course {self.title}>"
