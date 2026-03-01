from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.analytics.balance_service import BalanceService
import traceback

router = APIRouter(prefix="/balance", tags=["balance"])

@router.get("/curve")
async def get_balance_curve(
    user_id: int = Query(1),
    interval: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db)
):
    """Get balance curve data"""
    try:
        service = BalanceService(db, user_id)
        return service.get_balance_curve(interval)
    except Exception as e:
        print(f"Error in balance curve: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison")
async def get_balance_comparison(
    user_id: int = Query(1),
    interval: str = Query("month", regex="^(week|month)$"),
    db: Session = Depends(get_db)
):
    """Compare this period vs last period"""
    try:
        service = BalanceService(db, user_id)
        return service.get_comparison(interval)
    except Exception as e:
        print(f"Error in balance comparison: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
