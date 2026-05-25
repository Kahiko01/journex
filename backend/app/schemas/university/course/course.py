"""
Course Schemas for Journex University
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: int = 0
    image_url: Optional[str] = None
    pdf_filename: Optional[str] = None
    status: str = "published"
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    pdf_filename: Optional[str] = None
    status: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None

class CourseResponse(CourseBase):
    id: str
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
