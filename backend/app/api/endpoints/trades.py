"""
Trades endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.db.session import get_db
from app.models.trade import Trade
from app.api.deps.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trades", tags=["trades"])

@router.get("/")
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all trades for the current user"""
    try:
        trades = db.query(Trade).filter(
            Trade.user_id == current_user_id
        ).order_by(Trade.exit_time.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(trades)} trades for user {current_user_id}")
        return trades
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trade_id}")
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get a specific trade"""
    try:
        trade = db.query(Trade).filter(
            Trade.id == trade_id,
            Trade.user_id == current_user_id
        ).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return trade
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_trade(
    trade: dict,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new trade"""
    try:
        db_trade = Trade(
            **trade,
            user_id=current_user_id
        )
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        return db_trade
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{trade_id}")
async def update_trade(
    trade_id: int,
    trade_update: dict,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update a trade"""
    try:
        trade = db.query(Trade).filter(
            Trade.id == trade_id,
            Trade.user_id == current_user_id
        ).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        for key, value in trade_update.items():
            setattr(trade, key, value)
        
        db.commit()
        db.refresh(trade)
        return trade
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{trade_id}")
async def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete a trade"""
    try:
        trade = db.query(Trade).filter(
            Trade.id == trade_id,
            Trade.user_id == current_user_id
        ).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        db.delete(trade)
        db.commit()
        return {"message": "Trade deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))
