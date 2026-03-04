from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.models.trade import Trade
import numpy as np
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_analytics_dashboard(user_id: int = 1, db: Session = Depends(get_db)):
    """Get all analytics metrics"""
    try:
        # Get all trades for user
        trades = db.query(Trade).filter(Trade.user_id == user_id).all()
        
        # Calculate metrics
        metrics = calculate_trade_metrics(trades)
        equity_curve = calculate_equity_curve(trades)
        strategy_perf = calculate_strategy_performance(trades)
        
        return {
            "overview": metrics,
            "equity_curve": equity_curve,
            "strategy_performance": strategy_perf
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drawdown")
async def get_drawdown(user_id: int = 1, db: Session = Depends(get_db)):
    """Get drawdown analysis"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return calculate_drawdown(trades)

@router.get("/risk")
async def get_risk_metrics(user_id: int = 1, db: Session = Depends(get_db)):
    """Get risk metrics"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return calculate_risk_metrics(trades)

@router.get("/sessions")
async def get_session_analysis(user_id: int = 1, db: Session = Depends(get_db)):
    """Get session analysis"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return {"sessions": analyze_sessions(trades)}

@router.get("/r-stats")
async def get_r_multiple_stats(user_id: int = 1, db: Session = Depends(get_db)):
    """Get R-multiple statistics"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return calculate_r_multiple_stats(trades)

# Helper functions
def calculate_trade_metrics(trades):
    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_profit_loss": 0
        }
    
    closed_trades = [t for t in trades if t.exit_price]
    winning = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
    losing = [t for t in closed_trades if t.profit_loss and t.profit_loss < 0]
    
    total_pl = sum(t.profit_loss or 0 for t in closed_trades)
    
    return {
        "total_trades": len(closed_trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round((len(winning) / len(closed_trades) * 100) if closed_trades else 0, 2),
        "total_profit_loss": round(total_pl, 2)
    }

def calculate_equity_curve(trades):
    curve = []
    equity = 0
    
    sorted_trades = sorted([t for t in trades if t.exit_time], key=lambda x: x.exit_time)
    
    for trade in sorted_trades:
        if trade.profit_loss:
            equity += trade.profit_loss
            curve.append({
                "date": trade.exit_time.isoformat(),
                "equity": round(equity, 2)
            })
    
    return curve

def calculate_strategy_performance(trades):
    strategies = {}
    
    for trade in trades:
        if not trade.strategy or not trade.profit_loss:
            continue
        
        strat = trade.strategy
        if strat not in strategies:
            strategies[strat] = {"trades": 0, "wins": 0, "total_pl": 0}
        
        strategies[strat]["trades"] += 1
        strategies[strat]["total_pl"] += trade.profit_loss
        if trade.profit_loss > 0:
            strategies[strat]["wins"] += 1
    
    result = []
    for strat, data in strategies.items():
        result.append({
            "strategy": strat,
            "trades": data["trades"],
            "win_rate": round((data["wins"] / data["trades"] * 100), 2),
            "total_pl": round(data["total_pl"], 2)
        })
    
    return result

def calculate_drawdown(trades):
    # Simplified drawdown calculation
    return {
        "max_drawdown": 0,
        "max_drawdown_pct": 0,
        "avg_drawdown": 0,
        "current_drawdown": 0,
        "recovery_time": 0
    }

def calculate_risk_metrics(trades):
    return {
        "sharpe_ratio": 0,
        "sortino_ratio": 0,
        "avg_risk_per_trade": 0,
        "max_risk": 0,
        "risk_consistency": 100
    }

def analyze_sessions(trades):
    return []

def calculate_r_multiple_stats(trades):
    return {
        "avg_r": 0,
        "median_r": 0,
        "max_r": 0,
        "min_r": 0,
        "positive_r": 0,
        "negative_r": 0,
        "expectancy": 0
    }
"""
Analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.session import get_db
from app.models.trade import Trade

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_analytics_summary(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get basic analytics summary"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == user_id).all()
        
        if not trades:
            return {
                "total_pl": 0,
                "win_rate": 0,
                "total_trades": 0,
                "profit_factor": 0
            }
        
        winning_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in trades if t.profit_loss and t.profit_loss < 0]
        
        total_pl = sum(t.profit_loss or 0 for t in trades)
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        gross_profit = sum(t.profit_loss for t in winning_trades)
        gross_loss = abs(sum(t.profit_loss for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
        
        return {
            "total_pl": round(total_pl, 2),
            "win_rate": round(win_rate, 2),
            "total_trades": len(trades),
            "profit_factor": round(profit_factor, 2)
        }
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
