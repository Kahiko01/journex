"""
Certification Model for Journex University
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    
    # Certificate details
    certificate_number = Column(String(100), unique=True, nullable=False)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Achievement details
    grade = Column(String(20), nullable=True)  # Pass, Merit, Distinction
    score = Column(Integer, nullable=True)  # Final score percentage
    
    # Verification
    verification_hash = Column(String(200), unique=True, nullable=False)
    is_verified = Column(Boolean, default=True)
    
    # Metadata - renamed from 'metadata' to avoid SQLAlchemy reserved word
    certificate_metadata = Column(JSON, nullable=True)  # Additional certificate data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="certificates")
    course = relationship("Course", backref="certificates")
    
    def __init__(self, **kwargs):
        # Handle metadata renaming
        if 'metadata' in kwargs:
            kwargs['certificate_metadata'] = kwargs.pop('metadata')
        super().__init__(**kwargs)
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        if not self.verification_hash:
            self.verification_hash = self.generate_verification_hash()
    
    def generate_certificate_number(self) -> str:
        """Generate a unique certificate number"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"JRNX-{timestamp}-{unique_id}"
    
    def generate_verification_hash(self) -> str:
        """Generate a unique verification hash"""
        return str(uuid.uuid4()).replace('-', '')[:20].upper()
    
    def verify(self) -> bool:
        """Verify the certificate"""
        return self.is_verified
    
    def to_dict(self) -> dict:
        """Convert certificate to dictionary"""
        return {
            "id": self.id,
            "certificate_number": self.certificate_number,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "course_id": self.course_id,
            "course_title": self.course.title if self.course else None,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "grade": self.grade,
            "score": self.score,
            "verification_hash": self.verification_hash,
            "is_verified": self.is_verified
        }


class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template design
    template_html = Column(Text, nullable=False)
    template_css = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    default_duration_days = Column(Integer, nullable=True)  # Certificate validity in days
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    courses = relationship("Course", secondary="course_certificate_templates", backref="certificate_templates")


class CourseCertificateTemplate(Base):
    __tablename__ = "course_certificate_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"))
    template_id = Column(String(36), ForeignKey("certificate_templates.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
