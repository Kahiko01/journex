from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import uuid
import random
import string

router = APIRouter(prefix="/university/cohorts", tags=["university"])

# Simple in-memory storage
cohorts_db = []

@router.get("/")
async def list_cohorts():
    """List all cohorts"""
    return {"cohorts": cohorts_db, "total": len(cohorts_db)}

@router.post("/")
async def create_cohort(cohort_data: dict):
    """Create a new cohort"""
    # Generate slug
    slug = cohort_data['name'].lower().replace(' ', '-') + '-' + ''.join(random.choices(string.digits, k=4))
    
    cohort = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "current_students": 0,
        "status": "upcoming",
        **cohort_data
    }
    
    cohorts_db.append(cohort)
    return cohort

@router.get("/{cohort_id}")
async def get_cohort(cohort_id: str):
    """Get cohort details"""
    cohort = next((c for c in cohorts_db if c['id'] == cohort_id), None)
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return cohort
