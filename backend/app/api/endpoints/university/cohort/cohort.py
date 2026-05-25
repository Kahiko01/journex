"""
Cohort API Endpoints for Journex University
"""


from app.schemas.university.cohort import (
    CohortCreate, 
    CohortUpdate, 
    CohortResponse, 
    CohortDetailResponse,
    CohortJoinRequest,
    CohortMemberResponse,
    CohortLeaderboardResponse,
    UserProgressResponse,
    UserProgressUpdate
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.api.deps.auth import get_current_user, get_current_active_user
from app.models.user import User
from app.services.university.cohort.cohort_service import CohortService
from app.schemas.university.cohort import (
    CohortCreate, CohortUpdate, CohortResponse, CohortDetailResponse,
    CohortJoinRequest, CohortMemberResponse, CohortLeaderboardResponse,
    UserProgressResponse, UserProgressUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cohorts", tags=["university-cohorts"])
cohort_service = CohortService()

# ==================== Cohort Management ====================

@router.post("/", response_model=CohortResponse)
async def create_cohort(
    cohort_data: CohortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new cohort"""
    try:
        cohort = cohort_service.create_cohort(db, cohort_data, current_user.id)
        return cohort
    except Exception as e:
        logger.error(f"Error creating cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CohortResponse])
async def get_cohorts(
    skip: int = Query(0, description="Number of cohorts to skip"),
    limit: int = Query(100, description="Number of cohorts to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all cohorts (public ones and ones user is a member of)"""
    try:
        cohorts = cohort_service.get_cohorts(db, skip, limit)
        
        # Filter based on user's membership and public status
        result = []
        for cohort in cohorts:
            if not cohort.is_private or current_user.id in [m.id for m in cohort.members]:
                result.append(cohort)
        
        return result
    except Exception as e:
        logger.error(f"Error getting cohorts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my", response_model=List[CohortResponse])
async def get_my_cohorts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get cohorts the current user is a member of"""
    try:
        cohorts = cohort_service.get_user_cohorts(db, current_user.id)
        return cohorts
    except Exception as e:
        logger.error(f"Error getting user cohorts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cohort_id}", response_model=CohortDetailResponse)
async def get_cohort_detail(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed information about a specific cohort"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Check access (private cohorts only for members)
        if cohort.is_private and current_user.id not in [m.id for m in cohort.members]:
            raise HTTPException(status_code=403, detail="Access denied to private cohort")
        
        # Get members with their progress
        members = []
        for member in cohort.members:
            progress = cohort_service.get_member_progress(db, cohort_id, member.id)
            members.append({
                "user_id": member.id,
                "username": member.username,
                "avatar_url": member.avatar_url,
                "joined_at": next((j.joined_at for j in cohort.members if j.id == member.id), None),
                "progress": progress
            })
        
        # Get courses
        courses = []
        for cc in cohort.courses:
            courses.append({
                "id": cc.course.id,
                "title": cc.course.title,
                "required": cc.required,
                "due_date": cc.due_date
            })
        
        # Get leaderboard if enabled
        leaderboard = None
        if cohort.leaderboard_enabled:
            leaderboard = cohort_service.get_leaderboard(db, cohort_id)
        
        return {
            **cohort.__dict__,
            "members": members,
            "courses": courses,
            "leaderboard": leaderboard,
            "member_count": len(cohort.members),
            "course_count": len(cohort.courses)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cohort detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cohort_id}", response_model=CohortResponse)
async def update_cohort(
    cohort_id: str,
    updates: CohortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a cohort (creator only)"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Check if user is creator (first member)
        if current_user.id != cohort.members[0].id:
            raise HTTPException(status_code=403, detail="Only cohort creator can update")
        
        updated = cohort_service.update_cohort(db, cohort_id, updates)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cohort_id}")
async def delete_cohort(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a cohort (creator only)"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Check if user is creator (first member)
        if current_user.id != cohort.members[0].id:
            raise HTTPException(status_code=403, detail="Only cohort creator can delete")
        
        success = cohort_service.delete_cohort(db, cohort_id)
        if success:
            return {"message": "Cohort deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete cohort")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Membership Management ====================

@router.post("/{cohort_id}/join")
async def join_cohort(
    cohort_id: str,
    request: Optional[CohortJoinRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Join a cohort"""
    try:
        invite_code = request.invite_code if request else None
        success = cohort_service.join_cohort(db, cohort_id, current_user.id, invite_code)
        
        if success:
            return {"message": "Successfully joined cohort"}
        else:
            raise HTTPException(status_code=400, detail="Failed to join cohort")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{cohort_id}/leave")
async def leave_cohort(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Leave a cohort"""
    try:
        success = cohort_service.leave_cohort(db, cohort_id, current_user.id)
        
        if success:
            return {"message": "Successfully left cohort"}
        else:
            raise HTTPException(status_code=400, detail="Failed to leave cohort")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cohort_id}/members", response_model=List[CohortMemberResponse])
async def get_cohort_members(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get members of a cohort with their progress"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Check access
        if cohort.is_private and current_user.id not in [m.id for m in cohort.members]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        members = []
        for member in cohort.members:
            progress = cohort_service.get_member_progress(db, cohort_id, member.id)
            completed = all(p["completed"] for p in progress)
            
            members.append({
                "user_id": member.id,
                "username": member.username,
                "avatar_url": member.avatar_url,
                "joined_at": next((j.joined_at for j in cohort.members if j.id == member.id), None),
                "completed": completed,
                "completed_at": None,  # Would need to track this
                "progress_percentage": sum(p["completed"] for p in progress) / len(progress) * 100 if progress else 0
            })
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cohort members: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Progress Tracking ====================

@router.get("/{cohort_id}/progress", response_model=List[UserProgressResponse])
async def get_my_progress(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's progress in a cohort"""
    try:
        progress = cohort_service.get_member_progress(db, cohort_id, current_user.id)
        return progress
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/progress/{course_id}")
async def update_progress(
    course_id: str,
    update: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user progress for a course"""
    try:
        # This would need a progress service
        # For now, return placeholder
        return {"message": "Progress update endpoint - to be implemented"}
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Leaderboard ====================

@router.get("/{cohort_id}/leaderboard", response_model=CohortLeaderboardResponse)
async def get_cohort_leaderboard(
    cohort_id: str,
    refresh: bool = Query(False, description="Force refresh leaderboard"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get cohort leaderboard"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        if not cohort.leaderboard_enabled:
            raise HTTPException(status_code=403, detail="Leaderboard not enabled for this cohort")
        
        # Check access
        if cohort.is_private and current_user.id not in [m.id for m in cohort.members]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if refresh:
            leaderboard = cohort_service.update_leaderboard(db, cohort_id)
        else:
            leaderboard = cohort.leaderboard
        
        if not leaderboard:
            raise HTTPException(status_code=404, detail="Leaderboard not found")
        
        return {
            "rankings": leaderboard.rankings,
            "last_updated": leaderboard.last_updated
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{cohort_id}/leaderboard/refresh")
async def refresh_leaderboard(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually refresh the leaderboard"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Only creator or admins can refresh
        if current_user.id != cohort.members[0].id:
            raise HTTPException(status_code=403, detail="Only cohort creator can refresh leaderboard")
        
        leaderboard = cohort_service.update_leaderboard(db, cohort_id)
        if leaderboard:
            return {
                "message": "Leaderboard refreshed",
                "rankings": leaderboard.rankings,
                "last_updated": leaderboard.last_updated
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh leaderboard")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Invite System ====================

@router.get("/{cohort_id}/invite")
async def get_invite_code(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get invite code for a private cohort (creator only)"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Only creator can get invite code
        if current_user.id != cohort.members[0].id:
            raise HTTPException(status_code=403, detail="Only cohort creator can get invite code")
        
        if not cohort.is_private:
            return {"message": "Cohort is public, no invite code needed"}
        
        return {"invite_code": cohort.invite_code}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invite code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{cohort_id}/invite/regenerate")
async def regenerate_invite_code(
    cohort_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Regenerate invite code for a private cohort (creator only)"""
    try:
        cohort = cohort_service.get_cohort(db, cohort_id)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")
        
        # Only creator can regenerate
        if current_user.id != cohort.members[0].id:
            raise HTTPException(status_code=403, detail="Only cohort creator can regenerate invite code")
        
        if not cohort.is_private:
            return {"message": "Cohort is public, no invite code needed"}
        
        new_code = cohort_service.generate_invite_code()
        cohort.invite_code = new_code
        db.commit()
        
        return {"invite_code": new_code}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating invite code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
