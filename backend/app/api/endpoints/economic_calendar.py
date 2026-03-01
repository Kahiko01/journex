from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from app.services.calendar.economic_calendar import EconomicCalendarService
import traceback

router = APIRouter(prefix="/economic-calendar", tags=["economic-calendar"])

# Initialize service (in production, you'd use dependency injection)
calendar_service = EconomicCalendarService()

@router.get("/events")
async def get_events(
    currency: Optional[str] = Query(None, description="Filter by currency (USD, EUR, etc.)"),
    impact: Optional[str] = Query(None, description="Filter by impact (Low, Medium, High)"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)")
):
    """Get economic events with filters"""
    try:
        events = calendar_service.get_events(currency, impact, date_from, date_to)
        return {
            "events": events,
            "total": len(events),
            "filters": {
                "currency": currency,
                "impact": impact,
                "date_from": date_from,
                "date_to": date_to
            }
        }
    except Exception as e:
        print(f"Error getting events: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_today_events():
    """Get today's events"""
    try:
        events = calendar_service.get_today_events()
        return {
            "events": events,
            "total": len(events),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming")
async def get_upcoming_events(hours: int = Query(24, description="Hours to look ahead")):
    """Get upcoming high-impact events"""
    try:
        events = calendar_service.get_upcoming_high_impact(hours)
        return {
            "events": events,
            "total": len(events),
            "hours_ahead": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/{event_id}/relevant")
async def mark_event_relevant(
    event_id: int,
    user_id: int = Query(1),
    relevant: bool = Query(True)
):
    """Mark an event as relevant for a user"""
    try:
        event = calendar_service.mark_relevant(event_id, user_id, relevant)
        if event:
            return {"message": "Event updated", "event": event}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/currencies")
async def get_currencies():
    """Get list of available currencies"""
    return {
        "currencies": ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "NZD", "CHF"]
    }

@router.get("/impacts")
async def get_impacts():
    """Get list of impact levels"""
    return {
        "impacts": ["Low", "Medium", "High"]
    }
