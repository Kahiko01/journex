"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate, 
    UserResponse, 
    UserProfileResponse,
    UserSettingsUpdate, 
    PasswordChange, 
    Token
)
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.api.deps.auth import get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.get("/test")
async def test_auth():
    """Test endpoint to check if router is working"""
    return {"message": "Auth router is working"}

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Register a new user"""
    # Check if user exists
    user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    
    if user:
        if user.email == user_in.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login with username and password"""
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user info"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    *,
    db: Session = Depends(get_db),
    user_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update user profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    *,
    db: Session = Depends(get_db),
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Change user password"""
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.get("/settings", response_model=UserProfileResponse)
async def get_settings(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user settings"""
    return current_user

@router.put("/settings", response_model=UserProfileResponse)
async def update_settings(
    *,
    db: Session = Depends(get_db),
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update user settings"""
    update_data = settings.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/settings/reset")
async def reset_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Reset settings to defaults"""
    # Reset to defaults
    current_user.theme_preference = "dark"
    current_user.email_notifications = True
    current_user.push_notifications = True
    current_user.daily_report = False
    current_user.weekly_report = True
    current_user.risk_warnings = True
    current_user.default_timeframe = "1M"
    current_user.chart_preference = "candles"
    current_user.currency_display = "USD"
    current_user.profile_public = False
    current_user.show_portfolio = True
    current_user.show_trading_stats = True
    
    db.commit()
    
    return {"message": "Settings reset to defaults"}

@router.post("/logout")
async def logout() -> Any:
    """Logout (client-side token discard)"""
    return {"message": "Successfully logged out"}

@router.post("/verify-request")
async def request_verification(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Request email verification (placeholder for email service)"""
    return {"message": "Verification email sent"}

@router.get("/verify/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """Verify email address (placeholder)"""
    return {"message": "Email verified successfully"}
