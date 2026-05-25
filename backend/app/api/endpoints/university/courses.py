"""
Courses API Endpoints for Journex University
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import re
import uuid

from app.db.session import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.models.university import Course
from app.schemas.university import CourseCreate, CourseUpdate, CourseResponse

logger = logging.getLogger(__name__)

# THIS LINE WAS MISSING - ADD IT!
router = APIRouter(prefix="/courses", tags=["university-courses"])

@router.get("/", response_model=dict)
async def get_courses(
    skip: int = Query(0, description="Number of courses to skip"),
    limit: int = Query(100, description="Number of courses to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all courses"""
    try:
        query = db.query(Course)
        
        if category:
            query = query.filter(Course.category == category)
        if difficulty:
            query = query.filter(Course.difficulty == difficulty)
        
        total = query.count()
        courses = query.order_by(Course.created_at.desc()).offset(skip).limit(limit).all()
        
        # Convert SQLAlchemy models to dict for proper serialization
        courses_list = []
        for course in courses:
            courses_list.append({
                "id": course.id,
                "slug": course.slug,
                "title": course.title,
                "description": course.description,
                "category": course.category,
                "difficulty": course.difficulty,
                "duration_minutes": course.duration_minutes,
                "image_url": course.image_url,
                "pdf_filename": course.pdf_filename,
                "status": course.status,
                "learning_objectives": course.learning_objectives,
                "prerequisites": course.prerequisites,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None
            })
        
        return {
            "courses": courses_list,
            "total": total
        }
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{course_id}", response_model=dict)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific course by ID"""
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Convert to dict for proper serialization
        return {
            "id": course.id,
            "slug": course.slug,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "difficulty": course.difficulty,
            "duration_minutes": course.duration_minutes,
            "image_url": course.image_url,
            "pdf_filename": course.pdf_filename,
            "status": course.status,
            "learning_objectives": course.learning_objectives,
            "prerequisites": course.prerequisites,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slug/{slug}", response_model=dict)
async def get_course_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific course by slug"""
    try:
        course = db.query(Course).filter(Course.slug == slug).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Convert to dict for proper serialization
        return {
            "id": course.id,
            "slug": course.slug,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "difficulty": course.difficulty,
            "duration_minutes": course.duration_minutes,
            "image_url": course.image_url,
            "pdf_filename": course.pdf_filename,
            "status": course.status,
            "learning_objectives": course.learning_objectives,
            "prerequisites": course.prerequisites,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new course (admin only)"""
    if current_user.username not in ["testuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Generate slug from title
        slug = course.title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Check if slug exists
        existing = db.query(Course).filter(Course.slug == slug).first()
        if existing:
            base_slug = slug
            counter = 1
            while existing:
                slug = f"{base_slug}-{counter}"
                existing = db.query(Course).filter(Course.slug == slug).first()
                counter += 1
        
        # Create course
        new_course = Course(
            id=str(uuid.uuid4()),
            slug=slug,
            title=course.title,
            description=course.description,
            category=course.category,
            difficulty=course.difficulty,
            duration_minutes=course.duration_minutes,
            status="published",
            pdf_filename=course.pdf_filename,
            image_url=course.image_url,
            learning_objectives=course.learning_objectives,
            prerequisites=course.prerequisites
        )
        
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        
        # Return as dict
        return {
            "id": new_course.id,
            "slug": new_course.slug,
            "title": new_course.title,
            "description": new_course.description,
            "category": new_course.category,
            "difficulty": new_course.difficulty,
            "duration_minutes": new_course.duration_minutes,
            "image_url": new_course.image_url,
            "pdf_filename": new_course.pdf_filename,
            "status": new_course.status,
            "learning_objectives": new_course.learning_objectives,
            "prerequisites": new_course.prerequisites,
            "created_at": new_course.created_at.isoformat() if new_course.created_at else None,
            "updated_at": new_course.updated_at.isoformat() if new_course.updated_at else None
        }
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a course (admin only)"""
    if current_user.username not in ["testuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        update_data = course_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)
        
        db.commit()
        db.refresh(course)
        
        # Return as dict
        return {
            "id": course.id,
            "slug": course.slug,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "difficulty": course.difficulty,
            "duration_minutes": course.duration_minutes,
            "image_url": course.image_url,
            "pdf_filename": course.pdf_filename,
            "status": course.status,
            "learning_objectives": course.learning_objectives,
            "prerequisites": course.prerequisites,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a course (admin only)"""
    if current_user.username not in ["testuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        db.delete(course)
        db.commit()
        return {"message": "Course deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[str])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique course categories"""
    try:
        categories = db.query(Course.category).distinct().all()
        return [c[0] for c in categories if c[0]]
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
