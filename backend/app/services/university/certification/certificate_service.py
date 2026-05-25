"""
Certificate Service for Journex University
Handles certificate generation, verification, and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import uuid
import hashlib
import hmac
import os
from weasyprint import HTML
from jinja2 import Template
import qrcode
from io import BytesIO
import base64

from app.models.university import (
    Certification,
    CertificateTemplate,
    CourseCertificateTemplate,
    UserProgress,
    Course
)
from app.models.user import User
from app.schemas.university.certification import (
    CertificateCreate,
    CertificateUpdate,
    CertificateVerifyRequest,
    CertificateGenerateRequest
)

logger = logging.getLogger(__name__)

class CertificateService:
    
    def __init__(self):
        self.secret_key = os.getenv("CERTIFICATE_SECRET_KEY", "journex-cert-secret-key-change-in-production")
        self.base_url = os.getenv("BASE_URL", "http://localhost:3000")
        
    # ==================== Certificate Generation ====================
    
    def generate_certificate_number(self, user_id: int, course_id: str) -> str:
        """Generate a unique certificate number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"JRNX-{timestamp}-{unique_id}"
    
    def generate_verification_hash(self, user_id: int, course_id: str, certificate_number: str) -> str:
        """Generate a unique verification hash for the certificate"""
        data = f"{user_id}:{course_id}:{certificate_number}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()[:20].upper()
    
    def generate_qr_code(self, verification_url: str) -> str:
        """Generate QR code for certificate verification"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in HTML/PDF
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def calculate_grade(self, score: float) -> str:
        """Calculate grade based on score percentage"""
        if score >= 90:
            return "Distinction"
        elif score >= 75:
            return "Merit"
        elif score >= 60:
            return "Pass"
        else:
            return "Fail"
    
    def generate_certificate_html(self, user: User, course: Course, certificate: Certification, 
                                  template: Optional[CertificateTemplate] = None) -> str:
        """Generate HTML for certificate"""
        
        # Default template if none provided
        if not template:
            template_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Certificate of Achievement</title>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .certificate {
                        max-width: 800px;
                        margin: 40px auto;
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        overflow: hidden;
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 40px;
                        text-align: center;
                    }
                    .header h1 {
                        margin: 0;
                        font-size: 48px;
                        font-weight: 300;
                        letter-spacing: 2px;
                    }
                    .header h2 {
                        margin: 10px 0 0;
                        font-size: 24px;
                        font-weight: 300;
                        opacity: 0.9;
                    }
                    .content {
                        padding: 40px;
                        text-align: center;
                    }
                    .content h3 {
                        color: #666;
                        font-size: 18px;
                        font-weight: 400;
                        margin: 0 0 10px;
                    }
                    .content h4 {
                        color: #333;
                        font-size: 36px;
                        font-weight: 600;
                        margin: 0 0 20px;
                    }
                    .content p {
                        color: #666;
                        font-size: 16px;
                        line-height: 1.6;
                        margin: 0 0 30px;
                    }
                    .details {
                        display: flex;
                        justify-content: space-around;
                        margin: 40px 0;
                        padding: 20px 0;
                        border-top: 2px solid #eee;
                        border-bottom: 2px solid #eee;
                    }
                    .detail-item {
                        text-align: center;
                    }
                    .detail-label {
                        color: #999;
                        font-size: 14px;
                        margin-bottom: 5px;
                    }
                    .detail-value {
                        color: #333;
                        font-size: 18px;
                        font-weight: 600;
                    }
                    .qr-code {
                        margin: 30px 0;
                    }
                    .qr-code img {
                        width: 120px;
                        height: 120px;
                    }
                    .footer {
                        background: #f5f5f5;
                        padding: 20px;
                        text-align: center;
                        color: #999;
                        font-size: 12px;
                    }
                    .footer p {
                        margin: 5px 0;
                    }
                    .verification-hash {
                        font-family: monospace;
                        font-size: 12px;
                        color: #666;
                        background: #f5f5f5;
                        padding: 10px;
                        border-radius: 5px;
                        word-break: break-all;
                    }
                </style>
            </head>
            <body>
                <div class="certificate">
                    <div class="header">
                        <h1>JOURNEX</h1>
                        <h2>University</h2>
                    </div>
                    
                    <div class="content">
                        <h3>This certificate is proudly presented to</h3>
                        <h4>{{ user_name }}</h4>
                        
                        <p>for successfully completing the course</p>
                        <h4 style="font-size: 28px; color: #667eea;">{{ course_title }}</h4>
                        
                        <p>with a grade of <strong>{{ grade }}</strong> ({{ score }}%)</p>
                        
                        <div class="details">
                            <div class="detail-item">
                                <div class="detail-label">Certificate Number</div>
                                <div class="detail-value">{{ certificate_number }}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Issue Date</div>
                                <div class="detail-value">{{ issue_date }}</div>
                            </div>
                        </div>
                        
                        {% if qr_code %}
                        <div class="qr-code">
                            <img src="{{ qr_code }}" alt="Verification QR Code">
                        </div>
                        {% endif %}
                        
                        <div class="verification-hash">
                            Verification: {{ verification_hash }}
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>This certificate can be verified at {{ verification_url }}</p>
                        <p>© Journex University - All rights reserved</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            template_html = template.template_html
        
        # Calculate grade
        grade = self.calculate_grade(certificate.score or 0)
        
        # Generate verification URL
        verification_url = f"{self.base_url}/verify/{certificate.verification_hash}"
        
        # Generate QR code
        qr_code = self.generate_qr_code(verification_url)
        
        # Prepare template data
        template_data = {
            "user_name": user.full_name or user.username,
            "course_title": course.title,
            "certificate_number": certificate.certificate_number,
            "issue_date": certificate.issue_date.strftime("%B %d, %Y"),
            "grade": grade,
            "score": certificate.score or 0,
            "verification_hash": certificate.verification_hash,
            "verification_url": verification_url,
            "qr_code": qr_code
        }
        
        # Render template
        template = Template(template_html)
        return template.render(**template_data)
    
    def generate_certificate_pdf(self, html_content: str) -> bytes:
        """Generate PDF from HTML content"""
        try:
            pdf = HTML(string=html_content).write_pdf()
            return pdf
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise e
    
    def issue_certificate(self, db: Session, user_id: int, course_id: str, 
                         score: float, template_id: Optional[str] = None) -> Certification:
        """Issue a certificate to a user for completing a course"""
        
        # Check if certificate already exists
        existing = db.query(Certification).filter(
            Certification.user_id == user_id,
            Certification.course_id == course_id
        ).first()
        
        if existing:
            logger.info(f"Certificate already exists for user {user_id} course {course_id}")
            return existing
        
        # Get user and course
        user = db.query(User).filter(User.id == user_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not user or not course:
            raise ValueError("User or course not found")
        
        # Check if user has completed the course
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.course_id == course_id,
            UserProgress.completed == True
        ).first()
        
        if not progress and score < 60:  # Allow manual issuance with score
            raise ValueError("User has not completed the course requirements")
        
        # Generate certificate number and hash
        certificate_number = self.generate_certificate_number(user_id, course_id)
        verification_hash = self.generate_verification_hash(user_id, course_id, certificate_number)
        
        # Calculate grade
        grade = self.calculate_grade(score)
        
        # Create certificate
        certificate = Certification(
            user_id=user_id,
            course_id=course_id,
            certificate_number=certificate_number,
            issue_date=datetime.utcnow(),
            grade=grade,
            score=score,
            verification_hash=verification_hash,
            is_verified=True
        )
        
        db.add(certificate)
        db.commit()
        db.refresh(certificate)
        
        # Update user progress with certificate info
        if progress:
            progress.certificate_issued = True
            progress.certificate_id = certificate.id
            db.commit()
        
        logger.info(f"Certificate issued: {certificate_number} for user {user_id}")
        
        return certificate
    
    # ==================== Certificate Management ====================
    
    def get_certificate(self, db: Session, certificate_id: str) -> Optional[Certification]:
        """Get certificate by ID"""
        return db.query(Certification).filter(Certification.id == certificate_id).first()
    
    def get_certificate_by_number(self, db: Session, certificate_number: str) -> Optional[Certification]:
        """Get certificate by certificate number"""
        return db.query(Certification).filter(
            Certification.certificate_number == certificate_number
        ).first()
    
    def get_certificate_by_hash(self, db: Session, verification_hash: str) -> Optional[Certification]:
        """Get certificate by verification hash"""
        return db.query(Certification).filter(
            Certification.verification_hash == verification_hash
        ).first()
    
    def get_user_certificates(self, db: Session, user_id: int) -> List[Certification]:
        """Get all certificates for a user"""
        return db.query(Certification).filter(
            Certification.user_id == user_id
        ).order_by(desc(Certification.issue_date)).all()
    
    def get_course_certificates(self, db: Session, course_id: str) -> List[Certification]:
        """Get all certificates for a course"""
        return db.query(Certification).filter(
            Certification.course_id == course_id
        ).order_by(desc(Certification.issue_date)).all()
    
    def verify_certificate(self, db: Session, verification_hash: str) -> Dict[str, Any]:
        """Verify a certificate by its hash"""
        certificate = self.get_certificate_by_hash(db, verification_hash)
        
        if not certificate:
            return {
                "valid": False,
                "message": "Certificate not found"
            }
        
        # Check if certificate is still valid
        if certificate.expiry_date and certificate.expiry_date < datetime.utcnow():
            return {
                "valid": False,
                "message": "Certificate has expired",
                "certificate": certificate
            }
        
        # Get user and course details
        user = db.query(User).filter(User.id == certificate.user_id).first()
        course = db.query(Course).filter(Course.id == certificate.course_id).first()
        
        return {
            "valid": True,
            "message": "Certificate is valid",
            "certificate": {
                "certificate_number": certificate.certificate_number,
                "issue_date": certificate.issue_date.isoformat(),
                "grade": certificate.grade,
                "score": certificate.score,
                "user_name": user.full_name or user.username if user else "Unknown",
                "course_title": course.title if course else "Unknown"
            }
        }
    
    def revoke_certificate(self, db: Session, certificate_id: str, reason: str) -> bool:
        """Revoke a certificate"""
        certificate = self.get_certificate(db, certificate_id)
        if not certificate:
            return False
        
        certificate.is_verified = False
        certificate.metadata = {
            "revoked": True,
            "revoked_at": datetime.utcnow().isoformat(),
            "revoke_reason": reason
        }
        
        db.commit()
        logger.info(f"Certificate revoked: {certificate_id}")
        return True
    
    # ==================== Certificate Templates ====================
    
    def create_template(self, db: Session, name: str, description: str, 
                       template_html: str, template_css: Optional[str] = None,
                       default_duration_days: Optional[int] = None) -> CertificateTemplate:
        """Create a new certificate template"""
        template = CertificateTemplate(
            name=name,
            description=description,
            template_html=template_html,
            template_css=template_css,
            default_duration_days=default_duration_days,
            is_active=True
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Certificate template created: {name}")
        return template
    
    def get_templates(self, db: Session, active_only: bool = True) -> List[CertificateTemplate]:
        """Get all certificate templates"""
        query = db.query(CertificateTemplate)
        if active_only:
            query = query.filter(CertificateTemplate.is_active == True)
        return query.all()
    
    def assign_template_to_course(self, db: Session, course_id: str, template_id: str) -> bool:
        """Assign a certificate template to a course"""
        # Check if already assigned
        existing = db.query(CourseCertificateTemplate).filter(
            CourseCertificateTemplate.course_id == course_id,
            CourseCertificateTemplate.template_id == template_id
        ).first()
        
        if existing:
            return True
        
        assignment = CourseCertificateTemplate(
            course_id=course_id,
            template_id=template_id
        )
        
        db.add(assignment)
        db.commit()
        
        logger.info(f"Template {template_id} assigned to course {course_id}")
        return True
    
    def get_course_template(self, db: Session, course_id: str) -> Optional[CertificateTemplate]:
        """Get the certificate template for a course"""
        assignment = db.query(CourseCertificateTemplate).filter(
            CourseCertificateTemplate.course_id == course_id
        ).first()
        
        if assignment:
            return db.query(CertificateTemplate).filter(
                CertificateTemplate.id == assignment.template_id
            ).first()
        
        return None
    
    # ==================== Batch Operations ====================
    
    def issue_certificates_for_course(self, db: Session, course_id: str, 
                                      min_score: float = 60) -> List[Certification]:
        """Issue certificates to all users who completed a course"""
        # Get all completed progress for this course
        completed = db.query(UserProgress).filter(
            UserProgress.course_id == course_id,
            UserProgress.completed == True
        ).all()
        
        certificates = []
        for progress in completed:
            try:
                certificate = self.issue_certificate(
                    db, 
                    progress.user_id, 
                    course_id, 
                    progress.average_score or min_score
                )
                certificates.append(certificate)
            except Exception as e:
                logger.error(f"Error issuing certificate for user {progress.user_id}: {e}")
        
        return certificates
    
    def check_completion_and_issue(self, db: Session, user_id: int, course_id: str) -> Optional[Certification]:
        """Check if user has completed course and issue certificate automatically"""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.course_id == course_id
        ).first()
        
        if not progress or not progress.completed:
            return None
        
        # Check if certificate already issued
        existing = db.query(Certification).filter(
            Certification.user_id == user_id,
            Certification.course_id == course_id
        ).first()
        
        if existing:
            return existing
        
        # Issue certificate
        return self.issue_certificate(db, user_id, course_id, progress.average_score or 70)
    
    # ==================== Statistics ====================
    
    def get_certificate_statistics(self, db: Session) -> Dict[str, Any]:
        """Get certificate statistics"""
        total = db.query(Certification).count()
        verified = db.query(Certification).filter(Certification.is_verified == True).count()
        revoked = total - verified
        
        # Certificates by grade
        grades = {}
        for grade in ["Distinction", "Merit", "Pass", "Fail"]:
            count = db.query(Certification).filter(Certification.grade == grade).count()
            if count > 0:
                grades[grade] = count
        
        # Recent certificates
        recent = db.query(Certification).order_by(desc(Certification.issue_date)).limit(10).all()
        
        return {
            "total": total,
            "verified": verified,
            "revoked": revoked,
            "by_grade": grades,
            "recent": [
                {
                    "id": c.id,
                    "certificate_number": c.certificate_number,
                    "grade": c.grade,
                    "score": c.score,
                    "issue_date": c.issue_date.isoformat(),
                    "is_verified": c.is_verified
                }
                for c in recent
            ]
        }
    
    def get_user_certificate_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get certificate statistics for a user"""
        certificates = self.get_user_certificates(db, user_id)
        
        total = len(certificates)
        by_grade = {}
        
        for cert in certificates:
            if cert.grade not in by_grade:
                by_grade[cert.grade] = 0
            by_grade[cert.grade] += 1
        
        return {
            "total": total,
            "by_grade": by_grade,
            "latest": certificates[0] if certificates else None
        }
