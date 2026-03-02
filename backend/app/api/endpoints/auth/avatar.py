"""
Avatar upload endpoints
"""

from app.schemas.auth.user import AvatarResponse
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from PIL import Image

from app.db.session import get_db
from app.models.user import User
from app.api.deps.auth import get_current_user
from app.schemas.auth.user import AvatarResponse

router = APIRouter(prefix="/avatar", tags=["avatar"])

# Configuration
UPLOAD_DIR = "uploads/avatars"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=AvatarResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a user avatar"""
    try:
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Optimize image
        try:
            img = Image.open(file_path)
            # Resize if too large
            if img.height > 500 or img.width > 500:
                img.thumbnail((500, 500))
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                file_path = file_path.replace(file_ext, '.jpg')
                filename = filename.replace(file_ext, '.jpg')
                file_ext = '.jpg'
            img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            print(f"Image optimization error: {e}")
        
        # Generate URL
        avatar_url = f"/uploads/avatars/{filename}"
        
        # Delete old avatar if exists
        if current_user.avatar_url:
            old_path = os.path.join(UPLOAD_DIR, os.path.basename(current_user.avatar_url))
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # Update user
        current_user.avatar_url = avatar_url
        db.commit()
        
        return AvatarResponse(
            avatar_url=avatar_url,
            message="Avatar uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/remove")
async def remove_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user avatar"""
    if current_user.avatar_url:
        # Delete file
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(current_user.avatar_url))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Update user
        current_user.avatar_url = None
        db.commit()
        
        return {"message": "Avatar removed successfully"}
    
    return {"message": "No avatar to remove"}

@router.get("/defaults")
async def get_default_avatars():
    """Get list of default avatars"""
    defaults = [
        {"id": 1, "url": "/default-avatars/avatar1.png", "name": "Trader 1"},
        {"id": 2, "url": "/default-avatars/avatar2.png", "name": "Trader 2"},
        {"id": 3, "url": "/default-avatars/avatar3.png", "name": "Trader 3"},
        {"id": 4, "url": "/default-avatars/avatar4.png", "name": "Trader 4"},
    ]
    return {"defaults": defaults}
