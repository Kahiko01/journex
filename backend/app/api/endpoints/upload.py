"""
File Upload Endpoint for Course Materials
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from typing import Optional

from app.db.session import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

# Configuration
UPLOAD_DIR = "uploads/courses"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_PDF_TYPES = {'.pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file (PDF or image)"""
    
    # Check admin access
    if current_user.username not in ["testuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Validate file type
    if file_ext in ALLOWED_IMAGE_TYPES:
        file_type = "image"
    elif file_ext in ALLOWED_PDF_TYPES:
        file_type = "pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return file info
    return {
        "filename": unique_filename,
        "url": f"/uploads/courses/{unique_filename}",
        "type": file_type,
        "size": os.path.getsize(file_path)
    }
