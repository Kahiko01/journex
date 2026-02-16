from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeCreate(BaseModel):
    symbol: str
    direction: str  # 'long' or 'short'
    entry_price: float
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    lot_size: float
    strategy: Optional[str] = None
    emotion: Optional[str] = None
    notes: Optional[str] = None

class TradeResponse(TradeCreate):
    id: int
    user_id: int
    profit_loss: Optional[float] = None
    pips_gain: Optional[float] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True