"""
Advanced Analytics Endpoints
Provides comprehensive trading analytics including:
- Edge Quality Analysis
- Monte Carlo Simulation
- Trade Clustering
- Stability Metrics
- Improvement Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

from app.db.session import get_db
from app.models.trade import Trade
from app.api.deps.auth import get_current_user_id

# Import all analytics services
from app.services.analytics.edge_quality import EdgeQualityService
from app.services.analytics.monte_carlo import MonteCarloService
from app.services.analytics.trade_clustering import TradeClusteringService
from app.services.analytics.stability_metrics import StabilityMetricsService
from app.services.analytics.improvement_tracking import ImprovementTrackingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-analytics", tags=["advanced-analytics"])

# Initialize all services
edge_service = EdgeQualityService()
monte_carlo_service = MonteCarloService()
clustering_service = TradeClusteringService()
stability_service = StabilityMetricsService()
improvement_service = ImprovementTrackingService()

# ==================== EDGE QUALITY ANALYSIS ====================

@router.get("/edge-quality")
async def get_edge_quality_analysis(
    days: Optional[int] = Query(None, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get Edge Quality Analysis"""
    try:
        # Build query
        query = db.query(Trade).filter(Trade.user_id == current_user_id)
        
        # Apply date filter if specified
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(Trade.exit_time >= cutoff_date)
        
        # Order by exit time
        trades = query.order_by(Trade.exit_time).all()
        
        if not trades:
            return {
                "status": "no_data",
                "message": "No trades found for analysis",
                "data": edge_service._empty_response()
            }
        
        # Convert to dict for analysis
        trade_dicts = []
        for trade in trades:
            trade_dict = {
                'id': trade.id,
                'profit_loss': trade.profit_loss or 0,
                'r_multiple': trade.r_multiple or 0,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'strategy': trade.strategy,
                'emotion': trade.emotion,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
            }
            trade_dicts.append(trade_dict)
        
        # Run edge quality analysis
        analysis = edge_service.analyze_edge_quality(trade_dicts)
        
        return {
            "status": "success",
            "total_trades": len(trades),
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Edge quality analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edge-quality/simple")
async def get_simple_edge_metrics(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get simple edge metrics for quick display"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user_id).order_by(Trade.exit_time).all()
        
        if not trades:
            return {
                "expectancy": 0,
                "profit_factor": 0,
                "win_rate": 0,
                "total_trades": 0
            }
        
        # Calculate basic metrics
        profit_losses = [t.profit_loss or 0 for t in trades]
        winning_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]
        
        gross_profit = sum(t.profit_loss for t in winning_trades)
        gross_loss = abs(sum(t.profit_loss for t in trades if t.profit_loss and t.profit_loss < 0))
        
        expectancy = edge_service.formulas.calculate_expectancy([{'profit_loss': p} for p in profit_losses])
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        return {
            "expectancy": round(expectancy, 2),
            "profit_factor": round(profit_factor, 2),
            "win_rate": round(win_rate, 2),
            "total_trades": len(trades)
        }
        
    except Exception as e:
        logger.error(f"Simple edge metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MONTE CARLO SIMULATION ====================

@router.get("/monte-carlo")
async def get_monte_carlo_simulation(
    simulations: int = Query(1000, description="Number of simulations to run"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Run Monte Carlo simulation on trade sequences"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user_id).order_by(Trade.exit_time).all()
        
        if not trades or len(trades) < 10:
            return {
                "status": "no_data", 
                "message": "Need at least 10 trades for meaningful simulation",
                "total_trades": len(trades) if trades else 0
            }
        
        # Convert to dict
        trade_dicts = []
        for trade in trades:
            trade_dicts.append({
                'profit_loss': trade.profit_loss or 0,
                'r_multiple': trade.r_multiple or 0,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None
            })
        
        # Run simulation
        simulation = monte_carlo_service.simulate(trade_dicts, simulations)
        
        return {
            "status": "success",
            "total_trades": len(trades),
            "simulations_run": simulations,
            "simulation": simulation
        }
        
    except Exception as e:
        logger.error(f"Monte Carlo simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRADE CLUSTERING ====================

@router.get("/trade-clustering")
async def get_trade_clustering(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Analyze trade clusters and patterns"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user_id).order_by(Trade.exit_time).all()
        
        if not trades or len(trades) < 5:
            return {
                "status": "no_data", 
                "message": "Need at least 5 trades for clustering analysis",
                "total_trades": len(trades) if trades else 0
            }
        
        # Convert to dict
        trade_dicts = []
        for trade in trades:
            trade_dicts.append({
                'id': trade.id,
                'profit_loss': trade.profit_loss or 0,
                'r_multiple': trade.r_multiple or 0,
                'symbol': trade.symbol,
                'strategy': trade.strategy,
                'emotion': trade.emotion,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
            })
        
        # Run clustering analysis
        clustering = clustering_service.analyze_clusters(trade_dicts)
        
        return {
            "status": "success",
            "total_trades": len(trades),
            "clustering": clustering
        }
        
    except Exception as e:
        logger.error(f"Trade clustering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STABILITY METRICS ====================

@router.get("/stability-metrics")
async def get_stability_metrics(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Calculate performance stability metrics"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user_id).order_by(Trade.exit_time).all()
        
        if not trades or len(trades) < 10:
            return {
                "status": "no_data", 
                "message": "Need at least 10 trades for stability analysis",
                "total_trades": len(trades) if trades else 0
            }
        
        # Convert to dict
        trade_dicts = []
        for trade in trades:
            trade_dicts.append({
                'profit_loss': trade.profit_loss or 0,
                'r_multiple': trade.r_multiple or 0,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
            })
        
        # Run stability analysis
        stability = stability_service.analyze_stability(trade_dicts)
        
        return {
            "status": "success",
            "total_trades": len(trades),
            "stability": stability
        }
        
    except Exception as e:
        logger.error(f"Stability metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== IMPROVEMENT TRACKING ====================

@router.get("/improvement-tracking")
async def get_improvement_tracking(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Track trader improvement and decay over time"""
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user_id).order_by(Trade.exit_time).all()
        
        if not trades or len(trades) < 20:
            return {
                "status": "no_data", 
                "message": "Need at least 20 trades for improvement tracking",
                "total_trades": len(trades) if trades else 0
            }
        
        # Convert to dict
        trade_dicts = []
        for trade in trades:
            trade_dicts.append({
                'profit_loss': trade.profit_loss or 0,
                'r_multiple': trade.r_multiple or 0,
                'strategy': trade.strategy,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
            })
        
        # Run improvement analysis
        improvement = improvement_service.analyze_improvement(trade_dicts)
        
        return {
            "status": "success",
            "total_trades": len(trades),
            "improvement": improvement
        }
        
    except Exception as e:
        logger.error(f"Improvement tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CALENDAR ENDPOINT ====================

@router.get("/calendar/{year}/{month}")
async def get_calendar_data(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get calendar heatmap data for a specific month"""
    try:
        # Get trades for the specified month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        trades = db.query(Trade).filter(
            Trade.user_id == current_user_id,
            Trade.exit_time >= start_date,
            Trade.exit_time < end_date
        ).order_by(Trade.exit_time).all()
        
        # Create a map of dates to trades
        daily_trades = defaultdict(list)
        
        for trade in trades:
            if trade.exit_time:
                date_str = trade.exit_time.strftime('%Y-%m-%d')
                daily_trades[date_str].append(trade)
        
        # Get the first day of the month and number of days
        first_day = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        
        # Calculate the day of week for the first day (0 = Monday, 6 = Sunday)
        first_weekday = first_day.weekday()
        
        # Build the heatmap grid (6 weeks x 7 days)
        heatmap = []
        
        # Add empty cells for days before month starts
        week = []
        for i in range(first_weekday):
            week.append({"empty": True})
        
        # Fill in the days of the month
        for day in range(1, last_day + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            day_trades = daily_trades.get(date_str, [])
            
            if day_trades:
                # Calculate total P/L for the day
                total_pl = sum(t.profit_loss or 0 for t in day_trades)
                
                # Determine color based on P/L
                if total_pl > 0:
                    # Profitable day - green
                    if total_pl > 1000:
                        color = "bg-green-600"
                    elif total_pl > 500:
                        color = "bg-green-500"
                    elif total_pl > 100:
                        color = "bg-green-400"
                    else:
                        color = "bg-green-300"
                elif total_pl < 0:
                    # Losing day - red
                    if total_pl < -1000:
                        color = "bg-red-600"
                    elif total_pl < -500:
                        color = "bg-red-500"
                    elif total_pl < -100:
                        color = "bg-red-400"
                    else:
                        color = "bg-red-300"
                else:
                    # Break even - yellow
                    color = "bg-yellow-500"
                
                heatmap_day = {
                    "day": day,
                    "date": date_str,
                    "pl": round(total_pl, 2),
                    "trades": len(day_trades),
                    "color": color,
                    "icons": [],
                    "has_data": True
                }
            else:
                heatmap_day = {
                    "day": day,
                    "date": date_str,
                    "pl": 0,
                    "trades": 0,
                    "color": "bg-gray-700",
                    "icons": [],
                    "has_data": False
                }
            
            week.append(heatmap_day)
            
            # If we've filled a week (7 days), add it to heatmap and start a new week
            if len(week) == 7:
                heatmap.append(week)
                week = []
        
        # Add empty cells for remaining days
        if week:
            while len(week) < 7:
                week.append({"empty": True})
            heatmap.append(week)
        
        # Ensure we have exactly 6 weeks (some months need 6 rows)
        while len(heatmap) < 6:
            heatmap.append([{"empty": True} for _ in range(7)])
        
        return {
            "year": year,
            "month": month,
            "month_name": first_day.strftime('%B'),
            "heatmap": heatmap,
            "has_data": len(trades) > 0
        }
        
    except Exception as e:
        logger.error(f"Calendar data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HEALTH CHECK ====================

@router.get("/health")
async def analytics_health_check():
    """Check if analytics services are available"""
    return {
        "status": "healthy",
        "services": {
            "edge_quality": "available",
            "monte_carlo": "available",
            "trade_clustering": "available",
            "stability_metrics": "available",
            "improvement_tracking": "available"
        },
        "timestamp": datetime.now().isoformat()
    }
