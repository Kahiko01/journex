"""
Certification Schemas for Journex University
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class CertificationBase(BaseModel):
    certificate_number: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    grade: Optional[str] = None
    score: Optional[int] = None
    verification_hash: str
    is_verified: bool = True
    metadata: Optional[Dict[str, Any]] = None

class CertificationCreate(BaseModel):
    user_id: int
    course_id: str
    score: int
    grade: Optional[str] = None

class CertificationResponse(CertificationBase):
    id: str
    user_id: int
    course_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CertificateVerifyRequest(BaseModel):
    verification_hash: str
