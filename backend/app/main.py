from fastapi.staticfiles import StaticFiles
from app.api.endpoints.auth import avatar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Journex",
    description="Professional Trading Journal & Analytics Platform",
    version=os.getenv("VERSION", "2.5.0")
)

# CORS configuration
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

# ============== IMPORT ALL ROUTERS ==============

# Core endpoints
from app.api.endpoints.auth import auth
from app.api.endpoints import trades
app.include_router(avatar.router, prefix="/api/v1")
from app.api.endpoints import analytics
from app.api.endpoints import advanced_analytics
from app.api.endpoints import calendar
from app.api.endpoints import balance

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# AI endpoints
from app.api.endpoints import fast_ai
from app.api.endpoints import ai

# Trading tools
from app.api.endpoints import trading_plan
from app.api.endpoints import checklist

# External data
from app.api.endpoints import economic_calendar

# University/learning
from app.api.endpoints.university import courses
from app.api.endpoints.university import cohort
from app.api.endpoints.university import certification

# ============== REGISTER ALL ROUTERS ==============

# Auth & users
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

# Core trading functionality
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(advanced_analytics.router, prefix="/api/v1", tags=["advanced-analytics"])
app.include_router(calendar.router, prefix="/api/v1", tags=["calendar"])
app.include_router(balance.router, prefix="/api/v1", tags=["balance"])

# AI assistants
app.include_router(fast_ai.router, prefix="/api/v1", tags=["ai"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])

# Trading tools
app.include_router(trading_plan.router, prefix="/api/v1", tags=["trading-plan"])
app.include_router(checklist.router, prefix="/api/v1", tags=["checklist"])

# External data
app.include_router(economic_calendar.router, prefix="/api/v1", tags=["economic-calendar"])

# University/learning platform
app.include_router(courses.router, prefix="/api/v1", tags=["university"])
app.include_router(cohort.router, prefix="/api/v1", tags=["university"])
app.include_router(certification.router, prefix="/api/v1", tags=["university"])


# ============== SYSTEM ENDPOINTS ==============

@app.get("/", tags=["system"])
async def root():
    return {
        "project": "Journex",
        "message": "Welcome to Journex API",
        "status": "running",
        "version": os.getenv("VERSION", "2.5.0"),
        "docs_url": "/docs"
    }


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("VERSION", "2.5.0")
    }
