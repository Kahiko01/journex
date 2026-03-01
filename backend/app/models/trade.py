from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=1)
    
    # Trade details
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    lot_size = Column(Float, nullable=False)
    
    # Calculations
    profit_loss = Column(Float, nullable=True)
    r_multiple = Column(Float, nullable=True)
    
    # Metadata
    strategy = Column(String(100), nullable=True)
    emotion = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=True)
    mistakes = Column(JSON, nullable=True)
    
    # Timestamps
    entry_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
# Add these fields to the Trade class
mae = Column(Float, nullable=True)  # Maximum Adverse Excursion
mfe = Column(Float, nullable=True)  # Maximum Favorable Excursion
entry_slippage = Column(Float, nullable=True)
exit_slippage = Column(Float, nullable=True)
emotional_state = Column(String(50), nullable=True)
discipline_score = Column(Integer, nullable=True)
rule_violations = Column(JSON, nullable=True)
