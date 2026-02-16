from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from app.api.endpoints import trades
from app.api.endpoints import analytics
from app.api.endpoints import calendar
from app.api.endpoints.university import courses
from app.api.endpoints.university import cohort
from app.api.endpoints.university import certification

load_dotenv()

app = FastAPI(
    title="Journex",
    description="Trading Journal Platform",
    version=os.getenv("VERSION", "1.0.0")
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(calendar.router, prefix="/api/v1", tags=["calendar"])
app.include_router(courses.router, prefix="/api/v1")
app.include_router(cohort.router, prefix="/api/v1")
app.include_router(certification.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "project": "Journex",
        "message": "Welcome to Journex API",
        "status": "running",
        "version": os.getenv("VERSION", "1.0.0")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01"}
