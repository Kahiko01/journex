from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.api.endpoints.trades import trades_db
import calendar

router = APIRouter()

@router.get("/calendar/month/{year}/{month}")
async def get_month_calendar(year: int, month: int, user_id: int = Query(1)):
    """Get calendar data for a specific month"""
    
    # Filter trades for this user
    user_trades = [t for t in trades_db if t.get('user_id') == user_id]
    
    # Create a map of dates to trades
    trades_by_date = {}
    
    for trade in user_trades:
        # Only consider closed trades (with exit_time)
        if trade.get('exit_time'):
            try:
                # Parse the date from exit_time
                exit_time = trade['exit_time']
                if isinstance(exit_time, str):
                    if 'T' in exit_time:
                        date_str = exit_time.split('T')[0]
                    else:
                        date_str = exit_time[:10]
                    
                    if date_str not in trades_by_date:
                        trades_by_date[date_str] = []
                    trades_by_date[date_str].append(trade)
            except:
                pass
    
    # Generate calendar grid
    cal = calendar.monthcalendar(year, month)
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
                    daily_pl = 0
                    for trade in day_trades:
                        if trade['direction'] == 'long':
                            pl = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
                        else:
                            pl = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
                        daily_pl += pl
                    
                    # Determine color based on P/L
                    if daily_pl > 50:
                        color = "bg-green-700"
                    elif daily_pl > 0:
                        color = "bg-green-500"
                    elif daily_pl > -50:
                        color = "bg-red-400"
                    else:
                        color = "bg-red-600"
                    
                    week_data.append({
                        "day": day,
                        "date": date_str,
                        "pl": daily_pl,
                        "trades": len(day_trades),
                        "color": color,
                        "icons": ["🔥"] if len(day_trades) > 5 else [],
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
        'month_name': calendar.month_name[month],
        'heatmap': heatmap,
        'has_data': any(day['has_data'] for week in heatmap for day in week if not day.get('empty'))
    }

# Remove the refresh endpoint since it's not needed
