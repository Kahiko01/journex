"""
Cohort System Schemas for Journex University
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== Base Schemas ====================

class CohortBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    start_date: datetime
    end_date: Optional[datetime] = None
    max_members: int = Field(50, ge=1, le=1000)
    is_private: bool = False
    leaderboard_enabled: bool = True
    show_progress: bool = True

class CohortCreate(CohortBase):
    course_ids: List[str] = []

class CohortUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    end_date: Optional[datetime] = None
    max_members: Optional[int] = Field(None, ge=1, le=1000)
    is_private: Optional[bool] = None
    leaderboard_enabled: Optional[bool] = None
    show_progress: Optional[bool] = None

# ==================== Response Schemas ====================

class CohortResponse(CohortBase):
    id: str
    invite_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: int = 0
    course_count: int = 0
    
    class Config:
        from_attributes = True

class CohortDetailResponse(CohortResponse):
    members: List[Dict[str, Any]] = []
    courses: List[Dict[str, Any]] = []
    leaderboard: Optional[List[Dict[str, Any]]] = None

# ==================== Member Schemas ====================

class CohortMemberResponse(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    joined_at: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    completed_courses: int = 0
    total_courses: int = 0
    last_active: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CohortJoinRequest(BaseModel):
    invite_code: Optional[str] = None

# ==================== Progress Schemas ====================

class UserProgressBase(BaseModel):
    course_id: str
    time_spent_minutes: Optional[int] = 0
    module_completed: Optional[str] = None
    quiz_score: Optional[Dict[str, float]] = None
    completed: Optional[bool] = None

class UserProgressResponse(BaseModel):
    course_id: str
    course_title: str
    required: bool = True
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    time_spent_minutes: int = 0
    average_score: float = 0.0
    modules_completed: List[str] = []
    last_accessed: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProgressUpdate(BaseModel):
    course_id: str
    time_spent_minutes: Optional[int] = None
    module_completed: Optional[str] = None
    quiz_score: Optional[Dict[str, float]] = None
    completed: Optional[bool] = None

# ==================== Leaderboard Schemas ====================

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    progress_percentage: float
    completed_courses: int
    total_courses: int
    last_active: Optional[str] = None

class CohortLeaderboardResponse(BaseModel):
    rankings: List[LeaderboardEntry]
    last_updated: datetime

# ==================== Statistics Schemas ====================

class CohortStatisticsResponse(BaseModel):
    total_members: int
    average_progress: float
    completed_count: int
    completion_rate: float
    active_today: int
    active_week: int
    total_courses: int
