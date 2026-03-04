"""
Main application module
"""

from fastapi.staticfiles import StaticFiles
from app.api.endpoints.analytics import anonymous_dashboard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create FastAPI app FIRST - before any router inclusions
app = FastAPI(
    title="Journex",
    description="Professional Trading Journal & Analytics Platform",
    version=os.getenv("VERSION", "1.0.0")
)

# CORS configuration - configure app immediately after creation
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOW import all routers AFTER app is created
# Import notifications router
from app.api.endpoints.notifications import notifications as notifications_router
app.include_router(anonymous_dashboard.router, prefix="/api/v1")
from app.api.endpoints import ai
from app.api.endpoints import trading_plan
from app.api.endpoints import trades
from app.api.endpoints import checklist
# from app.api.endpoints import analytics  # Commented out
from app.api.endpoints import calendar
from app.api.endpoints import advanced_analytics
from app.api.endpoints import balance
from app.api.endpoints import economic_calendar
from app.api.endpoints.university import courses
from app.api.endpoints.university import cohort
from app.api.endpoints.university import certification
from app.api.endpoints.auth import auth
from app.api.endpoints.auth import avatar
from app.api.endpoints import fast_ai
from app.api.endpoints.analytics.anonymous_tracking import router as anonymous_tracking_router
# Serve static files (for PDFs, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
# Include notifications router
app.include_router(notifications_router.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(trading_plan.router, prefix="/api/v1", tags=["trading-plan"])
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(checklist.router, prefix="/api/v1", tags=["checklist"])
# app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])  # Commented out
app.include_router(calendar.router, prefix="/api/v1", tags=["calendar"])
app.include_router(advanced_analytics.router, prefix="/api/v1", tags=["advanced-analytics"])
app.include_router(balance.router, prefix="/api/v1", tags=["balance"])
app.include_router(economic_calendar.router, prefix="/api/v1", tags=["economic-calendar"])
app.include_router(courses.router, prefix="/api/v1", tags=["university"])
app.include_router(cohort.router, prefix="/api/v1", tags=["university"])
app.include_router(certification.router, prefix="/api/v1", tags=["university"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(avatar.router, prefix="/api/v1")
app.include_router(fast_ai.router, prefix="/api/v1")
app.include_router(anonymous_tracking_router, prefix="/api/v1")

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    return {
        "project": "Journex",
        "message": "Welcome to Journex API",
        "status": "running",
        "version": os.getenv("VERSION", "1.0.0")
    }

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
