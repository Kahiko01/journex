from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/university/certification", tags=["university"])

# In-memory storage
certificates_db = []
certification_levels_db = [
    {
        "id": "bronze-level",
        "name": "Bronze",
        "level_order": 1,
        "badge_color": "#CD7F32",
        "badge_icon": "/badges/bronze.png",
        "description": "Foundation of disciplined trading"
    },
    {
        "id": "silver-level",
        "name": "Silver",
        "level_order": 2,
        "badge_color": "#C0C0C0",
        "badge_icon": "/badges/silver.png",
        "description": "Consistent risk management"
    },
    {
        "id": "gold-level",
        "name": "Gold",
        "level_order": 3,
        "badge_color": "#FFD700",
        "badge_icon": "/badges/gold.png",
        "description": "Master of trading discipline"
    },
    {
        "id": "elite-level",
        "name": "Elite",
        "level_order": 4,
        "badge_color": "#9400D3",
        "badge_icon": "/badges/elite.png",
        "description": "Peak trading performance"
    }
]

@router.get("/levels")
async def get_certification_levels():
    """Get all certification levels"""
    return {"levels": certification_levels_db}

@router.post("/check/{user_id}")
async def check_certification_eligibility(user_id: str):
    """Check user's eligibility for all certification levels"""
    from app.services.university.certification_service import CertificationService
    from app.services.university.discipline_service import DisciplineScoreService
    
    cert_service = CertificationService()
    disc_service = DisciplineScoreService()
    
    # Get user stats (simulated - replace with actual DB query)
    user_stats = {
        "discipline_score": 85,
        "risk_consistency": 82,
        "avg_r_multiple": 0.9,
        "max_drawdown_percent": 12,
        "average_quiz_score": 88,
        "rule_violations": 3,
        "trades_analyzed": 75,
        "weeks_above_threshold": 4
    }
    
    # Check highest level
    result = cert_service.evaluate_for_highest_certification(user_stats)
    
    return {
        "user_id": user_id,
        "highest_eligible": result,
        "all_levels": {
            "bronze": cert_service.check_certification_eligibility(user_stats, "bronze"),
            "silver": cert_service.check_certification_eligibility(user_stats, "silver"),
            "gold": cert_service.check_certification_eligibility(user_stats, "gold"),
            "elite": cert_service.check_certification_eligibility(user_stats, "elite")
        }
    }

@router.post("/issue/{user_id}")
async def issue_certificate(user_id: str, level: str, cohort_id: Optional[str] = None):
    """Issue a certificate to a user"""
    from app.services.university.certification_service import CertificationService
    
    cert_service = CertificationService()
    
    # Check eligibility first
    user_stats = {
        "discipline_score": 85,
        "risk_consistency": 82,
        "avg_r_multiple": 0.9,
        "max_drawdown_percent": 12,
        "average_quiz_score": 88,
        "rule_violations": 3,
        "trades_analyzed": 75,
        "weeks_above_threshold": 4
    }
    
    eligibility = cert_service.check_certification_eligibility(user_stats, level)
    if not eligibility['eligible']:
        raise HTTPException(status_code=400, detail="Not eligible for this certification")
    
    # Generate certificate
    cert_number = cert_service.generate_certificate_number(user_id, level)
    verification_url = cert_service.generate_verification_url(cert_number)
    
    certificate = {
        "id": str(uuid.uuid4()),
        "certificate_number": cert_number,
        "user_id": user_id,
        "certification_level": level,
        "cohort_id": cohort_id,
        "issued_at": datetime.utcnow().isoformat(),
        "is_active": True,
        "public_verification_url": verification_url,
        "final_discipline_score": user_stats['discipline_score'],
        "final_risk_consistency": user_stats['risk_consistency'],
        "final_avg_r_multiple": user_stats['avg_r_multiple']
    }
    
    certificates_db.append(certificate)
    
    return certificate

@router.get("/verify/{certificate_number}")
async def verify_certificate(certificate_number: str):
    """Public endpoint to verify a certificate"""
    certificate = next((c for c in certificates_db if c['certificate_number'] == certificate_number), None)
    
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if not certificate.get('is_active', True):
        return {
            "valid": False,
            "message": "Certificate has been revoked",
            "certificate": certificate
        }
    
    return {
        "valid": True,
        "certificate": certificate
    }

@router.post("/revoke/{certificate_id}")
async def revoke_certificate(certificate_id: str, reason: str):
    """Revoke a certificate (admin only)"""
    certificate = next((c for c in certificates_db if c['id'] == certificate_id), None)
    
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    certificate['is_active'] = False
    certificate['revoked_at'] = datetime.utcnow().isoformat()
    certificate['revoke_reason'] = reason
    
    return {"message": "Certificate revoked", "certificate": certificate}

@router.get("/user/{user_id}")
async def get_user_certificates(user_id: str):
    """Get all certificates for a user"""
    user_certs = [c for c in certificates_db if c['user_id'] == user_id]
    
    return {
        "user_id": user_id,
        "certificates": user_certs,
        "count": len(user_certs)
    }
