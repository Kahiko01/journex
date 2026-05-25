"""
Social/Community Models for Journex
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, JSON, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class PublicProfile(Base):
    """Public trader profile (opt-in)"""
    __tablename__ = "public_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Profile visibility
    is_public = Column(Boolean, default=False)
    show_portfolio = Column(Boolean, default=True)
    show_trades = Column(Boolean, default=True)
    show_stats = Column(Boolean, default=True)
    
    # Bio and social links
    bio = Column(Text, nullable=True)
    trading_style = Column(String(100), nullable=True)
    favorite_markets = Column(JSON, nullable=True)
    social_links = Column(JSON, nullable=True)
    
    # Stats
    total_followers = Column(Integer, default=0)
    total_following = Column(Integer, default=0)
    total_strategies = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - simplified
    user = relationship("User", backref="public_profile")


class Follow(Base):
    """Follow relationship between traders"""
    __tablename__ = "follows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('follower_id', 'following_id', name='unique_follow'),)
    
    # Relationships - simplified
    follower = relationship("User", foreign_keys=[follower_id])
    following = relationship("User", foreign_keys=[following_id])


class Strategy(Base):
    """Shared trading strategy"""
    __tablename__ = "strategies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Strategy details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Strategy content
    entry_conditions = Column(JSON, nullable=True)
    exit_conditions = Column(JSON, nullable=True)
    risk_management = Column(JSON, nullable=True)
    examples = Column(JSON, nullable=True)
    
    # Media
    thumbnail_url = Column(String(500), nullable=True)
    chart_images = Column(JSON, nullable=True)
    
    # Stats
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    copies_count = Column(Integer, default=0)
    
    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="strategies")
    comments = relationship("StrategyComment", back_populates="strategy", cascade="all, delete-orphan")
    likes = relationship("StrategyLike", back_populates="strategy", cascade="all, delete-orphan")


class StrategyLike(Base):
    """Strategy likes"""
    __tablename__ = "strategy_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String(36), ForeignKey("strategies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('strategy_id', 'user_id', name='unique_like'),)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="likes")
    user = relationship("User")


class StrategyComment(Base):
    """Comments on strategies"""
    __tablename__ = "strategy_comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String(36), ForeignKey("strategies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("strategy_comments.id"), nullable=True)
    
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    is_edited = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    strategy = relationship("Strategy", back_populates="comments")
    user = relationship("User")
    replies = relationship("StrategyComment", backref="parent", remote_side=[id])


class LeaderboardEntry(Base):
    """Anonymized leaderboard entries"""
    __tablename__ = "leaderboard_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    period_type = Column(String(20), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    total_pl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    sharpe_ratio = Column(Float, default=0.0)
    
    rank = Column(Integer, nullable=True)
    is_anonymous = Column(Boolean, default=True)
    username_display = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="leaderboard_entries")


class ActivityFeed(Base):
    """User activity feed for social features"""
    __tablename__ = "activity_feeds"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_id = Column(String(36), nullable=True)
    target_type = Column(String(50), nullable=True)
    meta_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="activities")
