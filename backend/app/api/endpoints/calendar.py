from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import calendar as cal_module
from app.db.session import get_db
from app.models.trade import Trade

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/month/{year}/{month}")
async def get_month_calendar(
    year: int, 
    month: int, 
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get calendar data for a specific month"""
    try:
        # Get all trades for this user
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time.isnot(None),
            Trade.exit_price.isnot(None)
        ).all()
        
        # Create a map of dates to trades
        trades_by_date = {}
        
        for trade in trades:
            if trade.exit_time:
                date_str = trade.exit_time.strftime('%Y-%m-%d')
                if date_str not in trades_by_date:
                    trades_by_date[date_str] = []
                trades_by_date[date_str].append(trade)
        
        # Generate calendar grid
        cal = cal_module.monthcalendar(year, month)
        heatmap = []
        
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({"empty": True})
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    day_trades = trades_by_date.get(date_str, [])
                    
                    if day_trades:
                        # Calculate daily P/L
                        daily_pl = sum(t.profit_loss or 0 for t in day_trades)
                        
                        # Determine color based on P/L
                        if daily_pl > 0:
                            if daily_pl > 1000:
                                color = "bg-green-700"
                            elif daily_pl > 500:
                                color = "bg-green-600"
                            else:
                                color = "bg-green-500"
                        else:
                            if daily_pl < -1000:
                                color = "bg-red-700"
                            elif daily_pl < -500:
                                color = "bg-red-600"
                            else:
                                color = "bg-red-500"
                        
                        week_data.append({
                            "day": day,
                            "date": date_str,
                            "pl": round(daily_pl, 2),
                            "trades": len(day_trades),
                            "color": color,
                            "icons": [],
                            "has_data": True
                        })
                    else:
                        week_data.append({
                            "day": day,
                            "date": date_str,
                            "pl": 0,
                            "trades": 0,
                            "color": "bg-gray-700",
                            "icons": [],
                            "has_data": False
                        })
            heatmap.append(week_data)
        
        return {
            'year': year,
            'month': month,
            'month_name': cal_module.month_name[month],
            'heatmap': heatmap,
            'has_data': any(day['has_data'] for week in heatmap for day in week if not day.get('empty'))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/day/{date}")
async def get_day_details(
    date: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get detailed trades for a specific day"""
    try:
        # Parse the date
        target_date = datetime.strptime(date, '%Y-%m-%d')
        next_date = target_date.replace(hour=23, minute=59, second=59)
        
        # Get trades for that day
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time >= target_date,
            Trade.exit_time <= next_date
        ).all()
        
        return {
            'date': date,
            'trades': [
                {
                    'id': t.id,
                    'symbol': t.symbol,
                    'direction': t.direction,
                    'entry_price': t.entry_price,
                    'exit_price': t.exit_price,
                    'lot_size': t.lot_size,
                    'profit_loss': t.profit_loss,
                    'strategy': t.strategy,
                    'entry_time': t.entry_time.isoformat() if t.entry_time else None,
                    'exit_time': t.exit_time.isoformat() if t.exit_time else None
                }
                for t in trades
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
