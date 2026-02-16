from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/university/courses", tags=["university"])

# Temporary in-memory storage (will be replaced with database)
courses_db = []
modules_db = []
lessons_db = []

@router.get("/")
async def list_courses(
    level: Optional[str] = None,
    tag: Optional[str] = None,
    status: str = "published"
):
    """List all published courses with optional filters"""
    filtered = [c for c in courses_db if c.get("status") == status]
    
    if level:
        filtered = [c for c in filtered if c.get("level") == level]
    
    if tag:
        filtered = [c for c in filtered if tag in c.get("tags", [])]
    
    return {
        "courses": filtered,
        "total": len(filtered)
    }

@router.get("/{slug}")
async def get_course(slug: str):
    """Get detailed course information by slug"""
    course = next((c for c in courses_db if c.get("slug") == slug), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get modules for this course
    course_modules = [m for m in modules_db if m.get("course_id") == course["id"]]
    course_modules.sort(key=lambda x: x.get("order_index", 0))
    
    # Get lessons for each module
    for module in course_modules:
        module_lessons = [l for l in lessons_db if l.get("module_id") == module["id"]]
        module_lessons.sort(key=lambda x: x.get("order_index", 0))
        module["lessons"] = module_lessons
    
    course["modules"] = course_modules
    
    return course

@router.post("/")
async def create_course(course_data: dict):
    """Create a new course (instructor only)"""
    from uuid import uuid4
    
    course = {
        "id": str(uuid4()),
        "slug": course_data.get("slug") or course_data["title"].lower().replace(" ", "-"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        **course_data
    }
    
    courses_db.append(course)
    return course