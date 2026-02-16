from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.api.endpoints.trades import trades_db
from app.services.analytics.metrics import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/analytics/drawdown")
async def get_drawdown(user_id: int = Query(1)):
    """Get drawdown analysis"""
    try:
        user_trades = [t for t in trades_db if t.get('user_id') == user_id]
        return analytics_service.calculator.calculate_drawdown(user_trades)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/risk")
async def get_risk_metrics(user_id: int = Query(1)):
    """Get risk metrics (Sharpe, Sortino, etc.)"""
    try:
        user_trades = [t for t in trades_db if t.get('user_id') == user_id]
        return analytics_service.calculator.calculate_risk_metrics(user_trades)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/sessions")
async def get_session_analysis(user_id: int = Query(1)):
    """Get performance by trading session"""
    try:
        user_trades = [t for t in trades_db if t.get('user_id') == user_id]
        return {"sessions": analytics_service.calculator.analyze_sessions(user_trades)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/r-stats")
async def get_r_multiple_stats(user_id: int = Query(1)):
    """Get R-multiple statistics"""
    try:
        user_trades = [t for t in trades_db if t.get('user_id') == user_id]
        return analytics_service.calculator.calculate_r_multiple_stats(user_trades)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard")
async def get_full_dashboard(user_id: int = Query(1)):
    """Get all analytics for dashboard"""
    try:
        user_trades = [t for t in trades_db if t.get('user_id') == user_id]
        return analytics_service.get_dashboard_metrics(user_trades)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
