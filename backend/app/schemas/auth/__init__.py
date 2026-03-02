"""
Auth Schemas Package
Exports all authentication-related schemas
"""

from .user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    UserSettingsUpdate,
    PasswordChange,
    Token,
    TokenData,
    AvatarResponse
)

__all__ = [
    "UserBase",
    "UserCreate", 
    "UserLogin",
    "UserResponse",
    "UserProfileResponse",
    "UserSettingsUpdate",
    "PasswordChange",
    "Token",
    "TokenData",
    "AvatarResponse"
]
