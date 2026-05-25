"""
Course Service for Journex University
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import re

from app.models.university import Course
from app.schemas.university import CourseCreate

logger = logging.getLogger(__name__)

class CourseService:
    
    def generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from title"""
        slug = title.lower()
        # Replace spaces and special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def create_course(self, db: Session, course_data: CourseCreate) -> Course:
        """Create a new course"""
        # Generate slug from title
        slug = self.generate_slug(course_data.title)
        
        # Check if slug exists
        existing = db.query(Course).filter(Course.slug == slug).first()
        if existing:
            # Add a number to make it unique
            base_slug = slug
            counter = 1
            while existing:
                slug = f"{base_slug}-{counter}"
                existing = db.query(Course).filter(Course.slug == slug).first()
                counter += 1
        
        course = Course(
            slug=slug,
            title=course_data.title,
            description=course_data.description,
            category=course_data.category,
            difficulty=course_data.difficulty,
            duration_minutes=course_data.duration_minutes,
            image_url=course_data.image_url,
            pdf_filename=course_data.pdf_filename,
            status=course_data.status,
            learning_objectives=course_data.learning_objectives,
            prerequisites=course_data.prerequisites
        )
        
        db.add(course)
        db.commit()
        db.refresh(course)
        
        logger.info(f"Course created: {course.title} (slug: {course.slug})")
        return course
