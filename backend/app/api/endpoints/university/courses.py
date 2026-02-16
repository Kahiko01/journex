from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import uuid
from app.services.university.database import get_courses_db, get_modules_db, get_lessons_db

router = APIRouter(prefix="/university/courses", tags=["university"])

# Get the shared database instances
courses_db = get_courses_db()
modules_db = get_modules_db()
lessons_db = get_lessons_db()

@router.get("/")
async def list_courses(level: Optional[str] = None, tag: Optional[str] = None):
    """List all courses"""
    filtered = courses_db.copy()

    if level:
        filtered = [c for c in filtered if c.get("level") == level]

    if tag:
        filtered = [c for c in filtered if tag in c.get("tags", [])]

    return {"courses": filtered, "total": len(filtered)}

@router.get("/{slug}")
async def get_course(slug: str):
    course = next((c for c in courses_db if c.get("slug") == slug), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_modules = [m for m in modules_db if m.get("course_id") == course["id"]]
    course_modules.sort(key=lambda x: x.get("order_index", 0))

    for module in course_modules:
        module_lessons = [l for l in lessons_db if l.get("module_id") == module["id"]]
        module_lessons.sort(key=lambda x: x.get("order_index", 0))
        module["lessons"] = module_lessons

    course["modules"] = course_modules
    return course

@router.post("/")
async def create_course(course_data: dict):
    course = {
        "id": str(uuid.uuid4()),
        "slug": course_data.get("slug") or course_data["title"].lower().replace(" ", "-"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "status": "published",
        **course_data
    }

    courses_db.append(course)
    print(f"Course added: {course['title']}. Total courses: {len(courses_db)}")
    return course

@router.get("/debug/all")
async def debug_all_courses():
    """Debug endpoint to see all courses"""
    return {
        "courses": courses_db,
        "count": len(courses_db)
    }
