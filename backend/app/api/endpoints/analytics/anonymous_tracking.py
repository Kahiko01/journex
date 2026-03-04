"""
Anonymous Tracking API Endpoints
"""

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import uuid

from app.db.session import get_db
from app.services.analytics.anonymous.anonymous_tracking import AnonymousTrackingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/anonymous", tags=["anonymous-tracking"])

class TrackEventRequest(BaseModel):
    event_type: str
    page: Optional[str] = None
    component: Optional[str] = None
    action: Optional[str] = None
    value: Optional[str] = None
    load_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None  # This stays as 'metadata' in the API


@router.post("/track-event")
async def track_event(
    request: TrackEventRequest, 
    req: Request, 
    db: Session = Depends(get_db)
):
    """Track an anonymous event"""
    logger.info(f"Received track event: {request.event_type} - {request.component} - {request.action}")
    
    # Initialize tracking service
    service = AnonymousTrackingService()
    
    # Prepare headers
    headers = {
        'user-agent': req.headers.get('user-agent'),
        'x-forwarded-for': req.headers.get('x-forwarded-for'),
        'screen-size': req.headers.get('screen-size')
    }
    
    # Get or create anonymous session
    session_id = service.get_or_create_session(db, None, headers)
    
    # Track the event - metadata from request gets passed to event_data in the service
    service.track_event(
        db=db,
        session_id=session_id,
        event_type=request.event_type,
        page=request.page,
        component=request.component,
        action=request.action,
        value=request.value,
        load_time=request.load_time,
        metadata=request.metadata  # This is correct - the service will map it to event_data
    )
    
    logger.info(f"Event tracked for session {session_id}")
    
    return {
        "status": "tracked",
        "session_id": session_id
    }
