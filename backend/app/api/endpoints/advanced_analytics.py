from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.analytics.advanced_metrics import AdvancedMetricsService
from app.services.analytics.comparisons import ComparisonService
from app.services.analytics.export import ExportService
import traceback

router = APIRouter(prefix="/advanced-analytics", tags=["advanced-analytics"])

@router.get("/dashboard")
async def get_full_dashboard(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Complete analytics dashboard with all metrics"""
    try:
        service = AdvancedMetricsService(db, user_id)
        return {
            "core_metrics": service.calculate_core_metrics(),
            "risk_metrics": service.calculate_risk_metrics(),
            "rolling_metrics": service.calculate_rolling_metrics(),
            "time_analysis": service.calculate_time_analysis(),
            "mae_mfe": service.calculate_mae_mfe()
        }
    except Exception as e:
        print(f"ERROR in dashboard: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/{year}/{month}")
async def get_calendar(
    year: int,
    month: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get calendar heatmap for specific month"""
    try:
        service = AdvancedMetricsService(db, user_id)
        return {
            'year': year,
            'month': month,
            'heatmap': service.get_calendar_heatmap(year, month)
        }
    except Exception as e:
        print(f"ERROR in calendar: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparisons")
async def get_comparisons(
    user_id: int = Query(1),
    comparison_type: str = Query("strategy"),
    db: Session = Depends(get_db)
):
    """Get performance comparisons"""
    try:
        service = ComparisonService(db, user_id)
        return service.get_comparison(comparison_type)
    except Exception as e:
        print(f"ERROR in comparisons: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{format}")
async def export_analytics(
    format: str,
    user_id: int = Query(1),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export analytics report"""
    try:
        service = ExportService(db, user_id)
        if format == "csv":
            return service.export_csv(start_date, end_date, strategy)
        elif format == "pdf":
            return service.export_pdf(start_date, end_date, strategy)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
    except Exception as e:
        print(f"ERROR in export: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get optimized chart data for frontend"""
    try:
        service = AdvancedMetricsService(db, user_id)
        
        if chart_type == "equity_curve":
            return service.get_equity_curve_with_drawdown()
        elif chart_type == "distribution":
            return service.get_r_multiple_distribution()
        elif chart_type == "heatmap":
            return service.get_performance_heatmap()
        elif chart_type == "scatter":
            return service.get_risk_reward_scatter()
        else:
            raise HTTPException(status_code=400, detail="Invalid chart type")
    except Exception as e:
        print(f"ERROR in charts: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
