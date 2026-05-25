"""
Social/Community API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.db.session import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.models import social as models
from app.schemas.social import social as schemas
from app.models.trade import Trade

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["social"])

# ==================== Public Profiles ====================

@router.get("/profile/{user_id}", response_model=schemas.TraderProfileResponse)
async def get_trader_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a trader's public profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = db.query(models.PublicProfile).filter(
            models.PublicProfile.user_id == user_id
        ).first()
        
        if profile and not profile.is_public and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Profile is private")
        
        # Get trading stats if user allows
        stats = None
        if profile and profile.show_stats:
            from app.services.analytics.edge_quality import EdgeQualityService
            edge_service = EdgeQualityService()
            # Get user's trades and calculate stats
            trades = db.query(Trade).filter(Trade.user_id == user_id).all()
            if trades:
                stats = {
                    "total_trades": len(trades),
                    "win_rate": len([t for t in trades if t.profit_loss > 0]) / len(trades) * 100,
                    "total_pl": sum(t.profit_loss or 0 for t in trades),
                    "avg_r": sum(t.r_multiple or 0 for t in trades) / len(trades) if trades else 0
                }
        
        return {
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "is_public": profile.is_public if profile else False,
            "bio": profile.bio if profile else None,
            "trading_style": profile.trading_style if profile else None,
            "favorite_markets": profile.favorite_markets if profile else None,
            "social_links": profile.social_links if profile else None,
            "total_followers": profile.total_followers if profile else 0,
            "total_following": profile.total_following if profile else 0,
            "total_strategies": profile.total_strategies if profile else 0,
            "stats": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trader profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/username/{username}", response_model=schemas.TraderProfileResponse)
async def get_trader_profile_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a trader's public profile by username"""
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = db.query(models.PublicProfile).filter(
            models.PublicProfile.user_id == user.id
        ).first()
        
        if profile and not profile.is_public and current_user.id != user.id:
            raise HTTPException(status_code=403, detail="Profile is private")
        
        # Get trading stats if user allows
        stats = None
        if profile and profile.show_stats:
            from app.models.trade import Trade
            trades = db.query(Trade).filter(Trade.user_id == user.id).all()
            if trades:
                winning_trades = [t for t in trades if t.profit_loss > 0]
                stats = {
                    "total_trades": len(trades),
                    "win_rate": len(winning_trades) / len(trades) * 100 if trades else 0,
                    "total_pl": sum(t.profit_loss or 0 for t in trades),
                    "avg_r": sum(t.r_multiple or 0 for t in trades) / len(trades) if trades else 0
                }
        
        return {
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "is_public": profile.is_public if profile else False,
            "bio": profile.bio if profile else None,
            "trading_style": profile.trading_style if profile else None,
            "favorite_markets": profile.favorite_markets if profile else None,
            "social_links": profile.social_links if profile else None,
            "total_followers": profile.total_followers if profile else 0,
            "total_following": profile.total_following if profile else 0,
            "total_strategies": profile.total_strategies if profile else 0,
            "stats": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trader profile by username: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=schemas.PublicProfileResponse)
async def update_public_profile(
    profile_update: schemas.PublicProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update your public profile"""
    try:
        profile = db.query(models.PublicProfile).filter(
            models.PublicProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            profile = models.PublicProfile(user_id=current_user.id)
            db.add(profile)
        
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "username": current_user.username,
            "avatar_url": current_user.avatar_url,
            "is_public": profile.is_public,
            "show_portfolio": profile.show_portfolio,
            "show_trades": profile.show_trades,
            "show_stats": profile.show_stats,
            "bio": profile.bio,
            "trading_style": profile.trading_style,
            "favorite_markets": profile.favorite_markets,
            "social_links": profile.social_links,
            "total_followers": profile.total_followers,
            "total_following": profile.total_following,
            "total_strategies": profile.total_strategies,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Follow System ====================
# ... rest of the file continues unchanged

# ============ STRATEGY DETAIL ENDPOINTS ============

@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full strategy details with comments and interactions"""
    
    # Get strategy with creator info
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Increment view count
    strategy.views += 1
    db.commit()
    
    # Get creator profile
    creator = db.query(PublicProfile).filter(PublicProfile.user_id == strategy.user_id).first()
    
    # Check if current user liked this strategy
    is_liked = db.query(StrategyLike).filter(
        StrategyLike.strategy_id == strategy_id,
        StrategyLike.user_id == current_user.id
    ).first() is not None
    
    # Get comments with user info
    comments = db.query(StrategyComment).filter(
        StrategyComment.strategy_id == strategy_id
    ).order_by(StrategyComment.created_at.desc()).all()
    
    # Format comments with user profiles
    comments_data = []
    for comment in comments:
        commenter = db.query(PublicProfile).filter(PublicProfile.user_id == comment.user_id).first()
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "username": commenter.username if commenter else "unknown",
                "avatar": commenter.avatar_url if commenter else None,
                "display_name": commenter.display_name if commenter else None
            }
        })
    
    return {
        "strategy": {
            "id": strategy.id,
            "title": strategy.title,
            "description": strategy.description,
            "category": strategy.category,
            "tags": strategy.tags,
            "entry_rules": strategy.entry_rules,
            "exit_rules": strategy.exit_rules,
            "risk_management": strategy.risk_management,
            "timeframes": strategy.timeframes,
            "instruments": strategy.instruments,
            "likes": strategy.likes,
            "comments_count": strategy.comments_count,
            "views": strategy.views,
            "created_at": strategy.created_at,
            "updated_at": strategy.updated_at,
            "creator": {
                "username": creator.username if creator else "unknown",
                "avatar": creator.avatar_url if creator else None,
                "display_name": creator.display_name if creator else None,
                "trading_style": creator.trading_style if creator else None
            },
            "is_liked": is_liked
        },
        "comments": comments_data
    }

@router.post("/strategies/{strategy_id}/like")
async def like_strategy(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or unlike a strategy"""
    
    # Check if already liked
    existing_like = db.query(StrategyLike).filter(
        StrategyLike.strategy_id == strategy_id,
        StrategyLike.user_id == current_user.id
    ).first()
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        strategy.likes -= 1
        action = "unliked"
    else:
        # Like
        new_like = StrategyLike(
            strategy_id=strategy_id,
            user_id=current_user.id
        )
        db.add(new_like)
        strategy.likes += 1
        action = "liked"
        
        # Create activity feed entry
        activity = ActivityFeed(
            user_id=strategy.user_id,  # Notify strategy creator
            actor_id=current_user.id,
            type="like",
            strategy_id=strategy_id,
            content=f"{current_user.username} liked your strategy: {strategy.title}"
        )
        db.add(activity)
    
    db.commit()
    
    return {
        "liked": action == "liked",
        "likes_count": strategy.likes
    }

@router.post("/strategies/{strategy_id}/comment")
async def comment_on_strategy(
    strategy_id: int,
    comment_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a strategy"""
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Create comment
    comment = StrategyComment(
        strategy_id=strategy_id,
        user_id=current_user.id,
        content=comment_data.get("content", "")
    )
    db.add(comment)
    
    # Update comment count
    strategy.comments_count += 1
    db.commit()
    
    # Get user profile for response
    profile = db.query(PublicProfile).filter(PublicProfile.user_id == current_user.id).first()
    
    # Create activity feed entry
    activity = ActivityFeed(
        user_id=strategy.user_id,  # Notify strategy creator
        actor_id=current_user.id,
        type="comment",
        strategy_id=strategy_id,
        content=f"{current_user.username} commented on your strategy: {strategy.title}"
    )
    db.add(activity)
    db.commit()
    
    return {
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "username": profile.username if profile else current_user.username,
                "avatar": profile.avatar_url if profile else None,
                "display_name": profile.display_name if profile else None
            }
        },
        "comments_count": strategy.comments_count
    }

@router.delete("/strategies/{strategy_id}/comment/{comment_id}")
async def delete_comment(
    strategy_id: int,
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only by comment author or strategy creator)"""
    
    comment = db.query(StrategyComment).filter(
        StrategyComment.id == comment_id,
        StrategyComment.strategy_id == strategy_id
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    # Check permissions
    if comment.user_id != current_user.id and strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    strategy.comments_count -= 1
    db.commit()
    
    return {"message": "Comment deleted successfully"}

@router.get("/strategies/feed")
async def get_strategy_feed(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get strategies from followed users"""
    
    # Get users current user follows
    follows = db.query(Follow).filter(Follow.follower_id == current_user.id).all()
    followed_user_ids = [f.following_id for f in follows]
    
    # If not following anyone, show popular strategies
    if not followed_user_ids:
        strategies = db.query(Strategy).filter(
            Strategy.is_published == True
        ).order_by(
            Strategy.created_at.desc()
        ).limit(limit).offset(offset).all()
    else:
        # Show strategies from followed users
        strategies = db.query(Strategy).filter(
            Strategy.user_id.in_(followed_user_ids),
            Strategy.is_published == True
        ).order_by(
            Strategy.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    # Format strategies with creator info
    strategies_data = []
    for strategy in strategies:
        creator = db.query(PublicProfile).filter(PublicProfile.user_id == strategy.user_id).first()
        is_liked = db.query(StrategyLike).filter(
            StrategyLike.strategy_id == strategy.id,
            StrategyLike.user_id == current_user.id
        ).first() is not None
        
        strategies_data.append({
            "id": strategy.id,
            "title": strategy.title,
            "description": strategy.description[:200] + "..." if len(strategy.description) > 200 else strategy.description,
            "category": strategy.category,
            "tags": strategy.tags[:3] if strategy.tags else [],  # Show only first 3 tags
            "likes": strategy.likes,
            "comments_count": strategy.comments_count,
            "views": strategy.views,
            "created_at": strategy.created_at,
            "creator": {
                "username": creator.username if creator else "unknown",
                "avatar": creator.avatar_url if creator else None,
                "display_name": creator.display_name if creator else None
            },
            "is_liked": is_liked
        })
    
    return {
        "strategies": strategies_data,
        "total": len(strategies_data),
        "has_more": len(strategies_data) == limit
    }

# ============ STRATEGY DETAIL ENDPOINTS ============

@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full strategy details with comments and interactions"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Increment view count
    strategy.views += 1
    db.commit()
    
    # Get creator profile
    creator = db.query(PublicProfile).filter(PublicProfile.user_id == strategy.user_id).first()
    
    # Check if current user liked this strategy
    is_liked = db.query(StrategyLike).filter(
        StrategyLike.strategy_id == strategy_id,
        StrategyLike.user_id == current_user.id
    ).first() is not None
    
    # Get comments with user info
    comments = db.query(StrategyComment).filter(
        StrategyComment.strategy_id == strategy_id
    ).order_by(StrategyComment.created_at.desc()).all()
    
    # Format comments with user profiles
    comments_data = []
    for comment in comments:
        commenter = db.query(PublicProfile).filter(PublicProfile.user_id == comment.user_id).first()
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "username": commenter.username if commenter else "unknown",
                "avatar": commenter.avatar_url if commenter else None,
                "display_name": commenter.display_name if commenter else None
            }
        })
    
    return {
        "strategy": {
            "id": strategy.id,
            "title": strategy.title,
            "description": strategy.description,
            "category": strategy.category,
            "tags": strategy.tags,
            "entry_rules": strategy.entry_rules,
            "exit_rules": strategy.exit_rules,
            "risk_management": strategy.risk_management,
            "likes": strategy.likes,
            "comments_count": strategy.comments_count,
            "views": strategy.views,
            "created_at": strategy.created_at,
            "updated_at": strategy.updated_at,
            "creator": {
                "username": creator.username if creator else "unknown",
                "avatar": creator.avatar_url if creator else None,
                "display_name": creator.display_name if creator else None,
                "trading_style": creator.trading_style if creator else None
            },
            "is_liked": is_liked
        },
        "comments": comments_data
    }

@router.post("/strategies/{strategy_id}/like")
async def like_strategy(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or unlike a strategy"""
    
    # Check if already liked
    existing_like = db.query(StrategyLike).filter(
        StrategyLike.strategy_id == strategy_id,
        StrategyLike.user_id == current_user.id
    ).first()
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        strategy.likes -= 1
        action = "unliked"
    else:
        # Like
        new_like = StrategyLike(
            strategy_id=strategy_id,
            user_id=current_user.id
        )
        db.add(new_like)
        strategy.likes += 1
        action = "liked"
    
    db.commit()
    
    return {
        "liked": action == "liked",
        "likes_count": strategy.likes
    }

@router.post("/strategies/{strategy_id}/comment")
async def comment_on_strategy(
    strategy_id: int,
    comment_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a strategy"""
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Create comment
    comment = StrategyComment(
        strategy_id=strategy_id,
        user_id=current_user.id,
        content=comment_data.get("content", "")
    )
    db.add(comment)
    
    # Update comment count
    strategy.comments_count += 1
    db.commit()
    
    # Get user profile for response
    profile = db.query(PublicProfile).filter(PublicProfile.user_id == current_user.id).first()
    
    return {
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "username": profile.username if profile else current_user.username,
                "avatar": profile.avatar_url if profile else None,
                "display_name": profile.display_name if profile else None
            }
        },
        "comments_count": strategy.comments_count
    }
