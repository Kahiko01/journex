"""
User Model for Authentication
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Authentication
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(200), nullable=True)
    trading_experience = Column(String(50), nullable=True)
    preferred_markets = Column(String(200), nullable=True)
    
    # Stats
    total_trades = Column(Integer, default=0)
    total_pl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Settings and preferences
    theme_preference = Column(String(20), default="dark")  # dark, light, cyberpunk, high-contrast
    accent_color = Column(String(20), default="cyan")  # cyan, purple, blue, green, rose, amber
    font_size = Column(String(20), default="normal")  # small, normal, large
    animations_enabled = Column(Boolean, default=True)
    compact_mode = Column(Boolean, default=False)
    
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    daily_report = Column(Boolean, default=False)
    weekly_report = Column(Boolean, default=True)
    risk_warnings = Column(Boolean, default=True)
    
    # Display settings
    default_timeframe = Column(String(20), default="1M")  # 1W, 1M, 3M, 1Y, ALL
    chart_preference = Column(String(20), default="candles")  # candles, line, bar
    currency_display = Column(String(10), default="USD")  # USD, EUR, GBP
    
    # Privacy settings
    profile_public = Column(Boolean, default=False)
    show_portfolio = Column(Boolean, default=True)
    show_trading_stats = Column(Boolean, default=True)
    
    # Notification settings
    trade_confirmation = Column(Boolean, default=True)
    streak_alert = Column(Boolean, default=True)
    drawdown_alert = Column(Boolean, default=True)
    profit_target_alert = Column(Boolean, default=True)
    
    # Relationships
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    
    # Notification relationships
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    notification_settings = relationship("UserNotificationSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
