from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# In-memory database
trades_db = []
next_id = 1

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

class TradeResponse(TradeCreate):
    id: int
    user_id: int
    profit_loss: Optional[float] = None
    r_multiple: Optional[float] = None
    created_at: str

@router.post("/trades/", response_model=TradeResponse)
async def create_trade(trade: TradeCreate):
    global next_id
    now = datetime.now().isoformat()
    
    # Calculate profit/loss
    profit_loss = None
    r_multiple = None
    
    if trade.exit_price:
        if trade.direction == 'long':
            profit_loss = (trade.exit_price - trade.entry_price) * trade.lot_size
        else:
            profit_loss = (trade.entry_price - trade.exit_price) * trade.lot_size
        
        # Calculate R-multiple if stop loss exists
        if trade.stop_loss:
            if trade.direction == 'long':
                risk = abs(trade.entry_price - trade.stop_loss) * trade.lot_size
            else:
                risk = abs(trade.stop_loss - trade.entry_price) * trade.lot_size
            if risk > 0:
                r_multiple = profit_loss / risk
    
    trade_dict = {
        "id": next_id,
        "user_id": 1,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "stop_loss": trade.stop_loss,
        "take_profit": trade.take_profit,
        "lot_size": trade.lot_size,
        "strategy": trade.strategy,
        "emotion": trade.emotion,
        "rating": trade.rating,
        "entry_time": trade.entry_time or now,
        "exit_time": trade.exit_time,
        "profit_loss": profit_loss,
        "r_multiple": r_multiple,
        "created_at": now
    }
    
    trades_db.append(trade_dict)
    next_id += 1
    return trade_dict

@router.get("/trades/", response_model=List[TradeResponse])
async def get_trades():
    return trades_db

@router.get("/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int):
    for trade in trades_db:
        if trade["id"] == trade_id:
            return trade
    raise HTTPException(status_code=404, detail="Trade not found")

@router.put("/trades/{trade_id}", response_model=TradeResponse)
async def update_trade(trade_id: int, trade_update: TradeCreate):
    for trade in trades_db:
        if trade["id"] == trade_id:
            # Update fields
            update_data = trade_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    trade[key] = value
            
            # Recalculate profit/loss
            if trade.get('exit_price'):
                if trade['direction'] == 'long':
                    trade['profit_loss'] = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
                else:
                    trade['profit_loss'] = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
            return trade
    raise HTTPException(status_code=404, detail="Trade not found")

@router.delete("/trades/{trade_id}")
async def delete_trade(trade_id: int):
    global trades_db
    for i, trade in enumerate(trades_db):
        if trade["id"] == trade_id:
            trades_db.pop(i)
            return {"message": "Trade deleted"}
    raise HTTPException(status_code=404, detail="Trade not found")

@router.delete("/trades/")
async def delete_all_trades():
    global trades_db
    trades_db = []
    return {"message": "All trades deleted"}
