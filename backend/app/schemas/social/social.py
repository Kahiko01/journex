"""
Social/Community Schemas for Journex
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== Public Profile Schemas ====================

class PublicProfileBase(BaseModel):
    is_public: bool = False
    show_portfolio: bool = True
    show_trades: bool = True
    show_stats: bool = True
    bio: Optional[str] = None
    trading_style: Optional[str] = None
    favorite_markets: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None

class PublicProfileUpdate(BaseModel):
    is_public: Optional[bool] = None
    show_portfolio: Optional[bool] = None
    show_trades: Optional[bool] = None
    show_stats: Optional[bool] = None
    bio: Optional[str] = None
    trading_style: Optional[str] = None
    favorite_markets: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None

class PublicProfileResponse(PublicProfileBase):
    id: str
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    total_followers: int
    total_following: int
    total_strategies: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TraderProfileResponse(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    is_public: bool
    bio: Optional[str] = None
    trading_style: Optional[str] = None
    favorite_markets: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None
    total_followers: int
    total_following: int
    total_strategies: int
    stats: Optional[Dict[str, Any]] = None  # Trading stats if user allows
    
    class Config:
        from_attributes = True

# ==================== Follow Schemas ====================

class FollowResponse(BaseModel):
    id: str
    follower_id: int
    following_id: int
    follower_username: str
    following_username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FollowersListResponse(BaseModel):
    followers: List[TraderProfileResponse]
    total: int

class FollowingListResponse(BaseModel):
    following: List[TraderProfileResponse]
    total: int

# ==================== Strategy Schemas ====================

class StrategyBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    entry_conditions: Optional[Dict[str, Any]] = None
    exit_conditions: Optional[Dict[str, Any]] = None
    risk_management: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    thumbnail_url: Optional[str] = None
    chart_images: Optional[List[str]] = None

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    entry_conditions: Optional[Dict[str, Any]] = None
    exit_conditions: Optional[Dict[str, Any]] = None
    risk_management: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    thumbnail_url: Optional[str] = None
    chart_images: Optional[List[str]] = None
    is_published: Optional[bool] = None

class StrategyResponse(StrategyBase):
    id: str
    user_id: int
    author_username: str
    author_avatar: Optional[str] = None
    likes_count: int
    comments_count: int
    views_count: int
    copies_count: int
    is_featured: bool
    is_liked_by_user: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StrategyListResponse(BaseModel):
    strategies: List[StrategyResponse]
    total: int
    page: int
    pages: int

# ==================== Comment Schemas ====================

class StrategyCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[str] = None

class StrategyCommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class StrategyCommentResponse(BaseModel):
    id: str
    strategy_id: str
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    content: str
    likes_count: int
    parent_id: Optional[str] = None
    replies: List['StrategyCommentResponse'] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

StrategyCommentResponse.model_rebuild()

# ==================== Leaderboard Schemas ====================

class LeaderboardEntryResponse(BaseModel):
    user_id: int
    username: Optional[str] = None
    rank: int
    total_pl: float
    win_rate: float
    profit_factor: float
    total_trades: int
    sharpe_ratio: float
    is_anonymous: bool
    
    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    period_type: str
    period_start: datetime
    period_end: datetime
    entries: List[LeaderboardEntryResponse]

# ==================== Activity Feed Schemas ====================

class ActivityFeedResponse(BaseModel):
    id: str
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    action_type: str
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None  # Changed from metadata to meta_data
    created_at: datetime
    
    class Config:
        from_attributes = True
