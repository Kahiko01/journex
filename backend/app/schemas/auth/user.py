"""
User Schemas for Authentication
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# Create User (Signup)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

# Login Request
class UserLogin(BaseModel):
    username: str
    password: str

# Token Response
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# User Response (base)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    trading_experience: Optional[str] = None
    preferred_markets: Optional[str] = None
    total_trades: int
    total_pl: float
    win_rate: float
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Avatar Response
class AvatarResponse(BaseModel):
    avatar_url: str
    message: str

# User Settings Update
class UserSettingsUpdate(BaseModel):
    # Profile settings
    full_name: Optional[str] = None
    bio: Optional[str] = None
    trading_experience: Optional[str] = None
    preferred_markets: Optional[str] = None
    
    # Display settings
    theme_preference: Optional[str] = None
    accent_color: Optional[str] = None
    font_size: Optional[str] = None
    animations_enabled: Optional[bool] = None
    compact_mode: Optional[bool] = None
    default_timeframe: Optional[str] = None
    chart_preference: Optional[str] = None
    currency_display: Optional[str] = None
    
    # Notification settings
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    daily_report: Optional[bool] = None
    weekly_report: Optional[bool] = None
    risk_warnings: Optional[bool] = None
    trade_confirmation: Optional[bool] = None
    streak_alert: Optional[bool] = None
    drawdown_alert: Optional[bool] = None
    profit_target_alert: Optional[bool] = None
    
    # Privacy settings
    profile_public: Optional[bool] = None
    show_portfolio: Optional[bool] = None
    show_trading_stats: Optional[bool] = None

# User Profile Response (extends UserResponse)
class UserProfileResponse(UserResponse):
    theme_preference: str
    accent_color: str
    font_size: str
    animations_enabled: bool
    compact_mode: bool
    email_notifications: bool
    push_notifications: bool
    daily_report: bool
    weekly_report: bool
    risk_warnings: bool
    default_timeframe: str
    chart_preference: str
    currency_display: str
    profile_public: bool
    show_portfolio: bool
    show_trading_stats: bool
    trade_confirmation: bool
    streak_alert: bool
    drawdown_alert: bool
    profit_target_alert: bool
    
    class Config:
        from_attributes = True

# Password Change
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
