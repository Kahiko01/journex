from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()

@router.get("/courses/")
async def get_courses():
    return {
        "courses": [
            {
                "id": "1",
                "title": "Technical Analysis 101",
                "description": "Master the art of reading price charts and identifying patterns.",
                "category": "Technical Analysis",
                "difficulty": "Beginner",
                "duration_minutes": 45,
                "slug": "tech-analysis-101",
                "status": "published",
                "created_at": "2024-03-11"
            },
            {
                "id": "2",
                "title": "Risk Management Strategy",
                "description": "Learn how to protect your capital and manage trade sizing.",
                "category": "Risk Management",
                "difficulty": "Intermediate",
                "duration_minutes": 60,
                "slug": "risk-management",
                "status": "published",
                "created_at": "2024-03-11"
            }
        ]
    }
@router.get("/courses/{slug}")
async def get_course_detail(slug: str):
    # For now, we manually search our mock data
    # In the future, this will be a database query
    mock_courses = [
        {
            "id": "1",
            "title": "Technical Analysis 101",
            "description": "Master the art of reading price charts and identifying patterns.",
            "category": "Technical Analysis",
            "difficulty": "Beginner",
            "duration_minutes": 45,
            "slug": "tech-analysis-101",
            "lessons": [
                {"id": "l1", "title": "Introduction to Candlesticks", "duration": "10:00"},
                {"id": "l2", "title": "Support and Resistance", "duration": "15:00"},
                {"id": "l3", "title": "Trendline Mastery", "duration": "20:00"}
            ]
        },
        {
            "id": "2",
            "title": "Risk Management Strategy",
            "description": "Learn how to protect your capital and manage trade sizing.",
            "category": "Risk Management",
            "difficulty": "Intermediate",
            "duration_minutes": 60,
            "slug": "risk-management",
            "lessons": [
                {"id": "l4", "title": "The 1% Rule", "duration": "15:00"},
                {"id": "l5", "title": "Position Sizing Calculator", "duration": "25:00"}
            ]
        }
    ]
    
    course = next((c for c in mock_courses if c["slug"] == slug), None)
    if not course:
        return {"error": "Course not found"}, 404
    return course
