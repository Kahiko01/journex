from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.models.trade import Trade
from pydantic import BaseModel, validator
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trades", tags=["trades"])

class TradeCreate(BaseModel):
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    lot_size: float
    strategy: Optional[str] = None
    emotion: Optional[str] = None
    rating: Optional[int] = None
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None

class TradeResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    lot_size: float
    strategy: Optional[str] = None
    emotion: Optional[str] = None
    rating: Optional[int] = None
    profit_loss: Optional[float] = None
    r_multiple: Optional[float] = None
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None
    created_at: Optional[str] = None
    
    @validator('entry_time', 'exit_time', 'created_at', pre=True, always=True)
    def datetime_to_str(cls, v):
        """Convert datetime objects to ISO format strings"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

@router.post("/", response_model=TradeResponse)
async def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade"""
    try:
        logger.info(f"Received trade: {trade}")
        
        # Calculate profit/loss if exit price exists
        profit_loss = None
        if trade.exit_price:
            if trade.direction == 'long':
                profit_loss = (trade.exit_price - trade.entry_price) * trade.lot_size
            else:
                profit_loss = (trade.entry_price - trade.exit_price) * trade.lot_size
            logger.info(f"Calculated profit_loss: {profit_loss}")
        
        # Parse dates
        entry_time = None
        if trade.entry_time:
            try:
                entry_time = datetime.fromisoformat(trade.entry_time.replace('Z', '+00:00'))
                logger.info(f"Parsed entry_time: {entry_time}")
            except:
                entry_time = datetime.now()
        else:
            entry_time = datetime.now()
        
        exit_time = None
        if trade.exit_time:
            try:
                exit_time = datetime.fromisoformat(trade.exit_time.replace('Z', '+00:00'))
                logger.info(f"Parsed exit_time: {exit_time}")
            except:
                pass
        
        # Create database record
        db_trade = Trade(
            user_id=1,
            symbol=trade.symbol,
            direction=trade.direction,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            lot_size=trade.lot_size,
            strategy=trade.strategy,
            emotion=trade.emotion,
            rating=trade.rating,
            profit_loss=profit_loss,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        logger.info(f"Adding trade to database: {db_trade}")
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        logger.info(f"Trade added successfully with ID: {db_trade.id}")
        
        return db_trade
        
    except Exception as e:
        logger.error(f"Error creating trade: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TradeResponse])
async def get_trades(db: Session = Depends(get_db)):
    """Get all trades"""
    try:
        trades = db.query(Trade).all()
        logger.info(f"Retrieved {len(trades)} trades")
        return trades
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get a specific trade"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.delete("/{trade_id}")
async def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """Delete a trade"""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db.delete(trade)
    db.commit()
    logger.info(f"Deleted trade {trade_id}")
    return {"message": "Trade deleted"}

@router.delete("/")
async def delete_all_trades(db: Session = Depends(get_db)):
    """Delete all trades (use with caution)"""
    try:
        count = db.query(Trade).delete()
        db.commit()
        logger.info(f"Deleted {count} trades")
        return {"message": f"Deleted {count} trades"}
    except Exception as e:
        logger.error(f"Error deleting all trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))
