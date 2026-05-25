"""
Journex Main Application
Professional Trading Journal & Analytics Platform
"""
from app.api.endpoints.social import social as social_router
from app.api.endpoints.university import courses
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Journex",
    description="Professional Trading Journal & Analytics Platform",
    version=os.getenv("VERSION", "2.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== CORS Configuration ====================

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://journex.app",
    "https://www.journex.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Import All Routers ====================

# Core endpoints
from app.api.endpoints import ai
from app.api.endpoints import trading_plan
from app.api.endpoints import trades
from app.api.endpoints import upload
from app.api.endpoints import checklist
from app.api.endpoints import calendar
from app.api.endpoints import advanced_analytics
from app.api.endpoints import balance
from app.api.endpoints import economic_calendar

# Auth endpoints
from app.api.endpoints.auth import auth
from app.api.endpoints.auth import avatar

# AI endpoints
from app.api.endpoints import fast_ai

# University endpoints
from app.api.endpoints.university import courses
from app.api.endpoints.university import cohort
from app.api.endpoints.university import certification

# Notification endpoints
from app.api.endpoints.notifications import notifications

# Analytics tracking endpoints - FIXED IMPORTS
from app.api.endpoints.analytics.anonymous_tracking import router as anonymous_tracking_router
from app.api.endpoints.analytics.anonymous_dashboard import router as anonymous_dashboard_router

# Test endpoints (optional)
from app.api.endpoints.notifications import test_notifications

# ==================== Include All Routers ====================

# Core API routes
app.include_router(courses.router, prefix="/api/v1/university", tags=["university"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])
app.include_router(trading_plan.router, prefix="/api/v1", tags=["trading-plan"])
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(upload.router, prefix="/api/v1")
app.include_router(checklist.router, prefix="/api/v1", tags=["checklist"])
app.include_router(calendar.router, prefix="/api/v1", tags=["calendar"])
app.include_router(advanced_analytics.router, prefix="/api/v1", tags=["advanced-analytics"])
app.include_router(balance.router, prefix="/api/v1", tags=["balance"])
app.include_router(social_router.router, prefix="/api/v1")
app.include_router(economic_calendar.router, prefix="/api/v1", tags=["economic-calendar"])

# Auth routes
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(avatar.router, prefix="/api/v1", tags=["avatar"])

# AI routes
app.include_router(fast_ai.router, prefix="/api/v1", tags=["ai"])

# University routes
app.include_router(courses.router, prefix="/api/v1/university", tags=["university"])
app.include_router(cohort.router, prefix="/api/v1/university", tags=["university-cohorts"])
app.include_router(certification.router, prefix="/api/v1/university", tags=["university-certification"])

# Notification routes
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])

# Anonymous tracking routes - FIXED
app.include_router(anonymous_tracking_router, prefix="/api/v1", tags=["anonymous"])
app.include_router(anonymous_dashboard_router, prefix="/api/v1", tags=["anonymous-dashboard"])

# Test routes (optional - remove in production)
app.include_router(test_notifications.router, prefix="/api/v1", tags=["test"])

# ==================== Static Files ====================

# Create static directories if they don't exist
os.makedirs("static/courses", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)

# Mount static file directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Run when the application starts"""
    logger.info("=" * 50)
    logger.info("Journex API Starting Up...")
    logger.info(f"Version: {os.getenv('VERSION', '2.0.0')}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("=" * 50)

# ==================== Shutdown Event ====================

@app.on_event("shutdown")
async def shutdown_event():
    """Run when the application shuts down"""
    logger.info("=" * 50)
    logger.info("Journex API Shutting Down...")
    logger.info("=" * 50)

# ==================== Root Endpoints ====================
# ==================== Root Endpoints ====================

@app.get("/", tags=["system"])
async def root():
    """Welcome endpoint"""
    return {
        "project": "Journex",
        "message": "Welcome to Journex API",
        "status": "running",
        "version": os.getenv("VERSION", "2.0.0"),
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "connected",
        "api_version": os.getenv("VERSION", "2.0.0")
    }

@app.get("/api/v1/health", tags=["system"])
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": os.getenv("VERSION", "2.0.0"),
        "timestamp": datetime.utcnow().isoformat()
    }
