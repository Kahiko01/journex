"""
Cohort Service for Journex University
Manages learning groups, member progress, and leaderboards
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import logging
import uuid
import random
import string

from app.models.university import (
    Cohort, 
    CohortCourse, 
    CohortLeaderboard, 
    cohort_members,
    UserProgress,
    Course
)
from app.models.user import User
from app.schemas.university.cohort.cohort import CohortCreate, CohortUpdate

logger = logging.getLogger(__name__)

class CohortService:
    
    def generate_invite_code(self) -> str:
        """Generate a random invite code for private cohorts"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def generate_uuid(self) -> str:
        """Generate a UUID string"""
        return str(uuid.uuid4())
    
    # ==================== Cohort CRUD Operations ====================
    
    def create_cohort(self, db: Session, cohort_data: CohortCreate, creator_id: int) -> Cohort:
        """Create a new cohort"""
        try:
            cohort = Cohort(
                id=self.generate_uuid(),
                name=cohort_data.name,
                description=cohort_data.description,
                start_date=cohort_data.start_date,
                end_date=cohort_data.end_date,
                max_members=cohort_data.max_members,
                is_private=cohort_data.is_private,
                leaderboard_enabled=cohort_data.leaderboard_enabled,
                show_progress=cohort_data.show_progress,
                invite_code=self.generate_invite_code() if cohort_data.is_private else None
            )
            
            db.add(cohort)
            db.flush()  # Get the ID without committing
            
            # Add creator as first member
            stmt = cohort_members.insert().values(
                cohort_id=cohort.id,
                user_id=creator_id,
                joined_at=datetime.utcnow()
            )
            db.execute(stmt)
            
            # Add courses if provided
            if hasattr(cohort_data, 'course_ids') and cohort_data.course_ids:
                for course_id in cohort_data.course_ids:
                    cohort_course = CohortCourse(
                        id=self.generate_uuid(),
                        cohort_id=cohort.id,
                        course_id=course_id,
                        required=True
                    )
                    db.add(cohort_course)
            
            # Create leaderboard entry
            leaderboard = CohortLeaderboard(
                id=self.generate_uuid(),
                cohort_id=cohort.id,
                rankings=[]
            )
            db.add(leaderboard)
            
            db.commit()
            db.refresh(cohort)
            
            logger.info(f"Cohort created: {cohort.name} (ID: {cohort.id}) by user {creator_id}")
            return cohort
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating cohort: {e}")
            raise e
    
    def get_cohort(self, db: Session, cohort_id: str) -> Optional[Cohort]:
        """Get cohort by ID"""
        return db.query(Cohort).filter(Cohort.id == cohort_id).first()
    
    def get_cohorts(self, db: Session, skip: int = 0, limit: int = 100, include_private: bool = False) -> List[Cohort]:
        """Get all cohorts (public only by default)"""
        query = db.query(Cohort)
        if not include_private:
            query = query.filter(Cohort.is_private == False)
        return query.order_by(Cohort.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_cohorts(self, db: Session, user_id: int) -> List[Cohort]:
        """Get all cohorts a user is a member of"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.cohorts
    
    def update_cohort(self, db: Session, cohort_id: str, updates: CohortUpdate) -> Optional[Cohort]:
        """Update cohort details"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        
        # Handle special fields
        if 'is_private' in update_data and update_data['is_private'] and not cohort.invite_code:
            update_data['invite_code'] = self.generate_invite_code()
        
        for field, value in update_data.items():
            setattr(cohort, field, value)
        
        cohort.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cohort)
        
        logger.info(f"Cohort updated: {cohort.id}")
        return cohort
    
    def delete_cohort(self, db: Session, cohort_id: str) -> bool:
        """Delete a cohort"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return False
        
        try:
            db.delete(cohort)
            db.commit()
            logger.info(f"Cohort deleted: {cohort_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting cohort: {e}")
            return False
    
    # ==================== Membership Management ====================
    
    def join_cohort(self, db: Session, cohort_id: str, user_id: int, invite_code: Optional[str] = None) -> Tuple[bool, str]:
        """Join a cohort. Returns (success, message)"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return False, "Cohort not found"
        
        # Check if private and verify invite code
        if cohort.is_private and cohort.invite_code != invite_code:
            return False, "Invalid invite code for private cohort"
        
        # Check if already a member
        existing = db.execute(
            cohort_members.select().where(
                and_(
                    cohort_members.c.cohort_id == cohort_id,
                    cohort_members.c.user_id == user_id
                )
            )
        ).first()
        
        if existing:
            return False, "Already a member of this cohort"
        
        # Check max members
        member_count = db.execute(
            cohort_members.select().where(cohort_members.c.cohort_id == cohort_id)
        ).rowcount
        
        if member_count >= cohort.max_members:
            return False, f"Cohort has reached maximum capacity ({cohort.max_members})"
        
        # Add member
        stmt = cohort_members.insert().values(
            cohort_id=cohort_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.execute(stmt)
        db.commit()
        
        logger.info(f"User {user_id} joined cohort {cohort_id}")
        return True, "Successfully joined cohort"
    
    def leave_cohort(self, db: Session, cohort_id: str, user_id: int) -> Tuple[bool, str]:
        """Leave a cohort. Returns (success, message)"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return False, "Cohort not found"
        
        # Check if member
        existing = db.execute(
            cohort_members.select().where(
                and_(
                    cohort_members.c.cohort_id == cohort_id,
                    cohort_members.c.user_id == user_id
                )
            )
        ).first()
        
        if not existing:
            return False, "Not a member of this cohort"
        
        # Check if creator (first member) - can't leave, must delete cohort
        first_member = db.execute(
            cohort_members.select()
            .where(cohort_members.c.cohort_id == cohort_id)
            .order_by(cohort_members.c.joined_at)
            .limit(1)
        ).first()
        
        if first_member and first_member.user_id == user_id:
            return False, "Creator cannot leave cohort. Delete the cohort instead."
        
        # Remove member
        stmt = cohort_members.delete().where(
            and_(
                cohort_members.c.cohort_id == cohort_id,
                cohort_members.c.user_id == user_id
            )
        )
        db.execute(stmt)
        db.commit()
        
        logger.info(f"User {user_id} left cohort {cohort_id}")
        return True, "Successfully left cohort"
    
    def get_cohort_members(self, db: Session, cohort_id: str) -> List[Dict[str, Any]]:
        """Get all members of a cohort with their progress"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return []
        
        members = []
        for member in cohort.members:
            progress = self.get_member_progress(db, cohort_id, member.id)
            completed_courses = sum(1 for p in progress if p['completed'])
            total_courses = len(progress)
            progress_percentage = (completed_courses / total_courses * 100) if total_courses > 0 else 0
            
            members.append({
                "user_id": member.id,
                "username": member.username,
                "avatar_url": member.avatar_url,
                "joined_at": self._get_join_date(db, cohort_id, member.id),
                "completed_courses": completed_courses,
                "total_courses": total_courses,
                "progress_percentage": round(progress_percentage, 1),
                "last_active": self._get_last_active(db, member.id)
            })
        
        return members
    
    def _get_join_date(self, db: Session, cohort_id: str, user_id: int) -> Optional[datetime]:
        """Get the date a user joined a cohort"""
        result = db.execute(
            cohort_members.select().where(
                and_(
                    cohort_members.c.cohort_id == cohort_id,
                    cohort_members.c.user_id == user_id
                )
            )
        ).first()
        return result.joined_at if result else None
    
    def _get_last_active(self, db: Session, user_id: int) -> Optional[datetime]:
        """Get user's last active timestamp"""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).order_by(UserProgress.last_accessed.desc()).first()
        
        return progress.last_accessed if progress else None
    
    # ==================== Course Management ====================
    
    def add_course_to_cohort(self, db: Session, cohort_id: str, course_id: str, required: bool = True) -> bool:
        """Add a course to a cohort"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return False
        
        # Check if course already exists
        existing = db.query(CohortCourse).filter(
            CohortCourse.cohort_id == cohort_id,
            CohortCourse.course_id == course_id
        ).first()
        
        if existing:
            return False
        
        cohort_course = CohortCourse(
            id=self.generate_uuid(),
            cohort_id=cohort_id,
            course_id=course_id,
            required=required
        )
        db.add(cohort_course)
        db.commit()
        
        logger.info(f"Course {course_id} added to cohort {cohort_id}")
        return True
    
    def remove_course_from_cohort(self, db: Session, cohort_id: str, course_id: str) -> bool:
        """Remove a course from a cohort"""
        result = db.query(CohortCourse).filter(
            CohortCourse.cohort_id == cohort_id,
            CohortCourse.course_id == course_id
        ).delete()
        
        db.commit()
        return result > 0
    
    def get_cohort_courses(self, db: Session, cohort_id: str) -> List[Dict[str, Any]]:
        """Get all courses in a cohort with their status"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return []
        
        courses = []
        for cc in cohort.courses:
            courses.append({
                "id": cc.course.id,
                "title": cc.course.title,
                "description": cc.course.description,
                "category": cc.course.category,
                "difficulty": cc.course.difficulty,
                "duration_minutes": cc.course.duration_minutes,
                "required": cc.required,
                "due_date": cc.due_date
            })
        
        return courses
    
    # ==================== Progress Tracking ====================
    
    def get_member_progress(self, db: Session, cohort_id: str, user_id: int) -> List[Dict[str, Any]]:
        """Get progress for a member in a cohort"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return []
        
        progress = []
        for cc in cohort.courses:
            user_progress = db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.course_id == cc.course_id
            ).first()
            
            # Get course details
            course = db.query(Course).filter(Course.id == cc.course_id).first()
            
            progress.append({
                "course_id": cc.course_id,
                "course_title": course.title if course else "Unknown Course",
                "required": cc.required,
                "due_date": cc.due_date,
                "completed": user_progress.completed if user_progress else False,
                "completed_at": user_progress.completed_at if user_progress else None,
                "time_spent_minutes": user_progress.time_spent_minutes if user_progress else 0,
                "average_score": user_progress.average_score if user_progress else 0,
                "modules_completed": user_progress.modules_completed if user_progress else [],
                "last_accessed": user_progress.last_accessed if user_progress else None
            })
        
        return progress
    
    def update_course_progress(self, db: Session, user_id: int, course_id: str, 
                              time_spent: Optional[int] = None,
                              module_completed: Optional[str] = None,
                              quiz_score: Optional[Dict[str, float]] = None,
                              mark_completed: bool = False) -> Optional[UserProgress]:
        """Update user progress for a specific course"""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.course_id == course_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                id=self.generate_uuid(),
                user_id=user_id,
                course_id=course_id
            )
            db.add(progress)
        
        # Update time spent
        if time_spent:
            progress.time_spent_minutes += time_spent
        
        # Update modules completed
        if module_completed and module_completed not in progress.modules_completed:
            modules = progress.modules_completed.copy() if progress.modules_completed else []
            modules.append(module_completed)
            progress.modules_completed = modules
        
        # Update quiz scores
        if quiz_score:
            scores = progress.quiz_scores.copy() if progress.quiz_scores else {}
            scores.update(quiz_score)
            progress.quiz_scores = scores
            
            # Calculate average score
            if scores:
                progress.average_score = sum(scores.values()) / len(scores)
        
        # Mark as completed if all modules done or explicitly requested
        if mark_completed:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        
        progress.last_accessed = datetime.utcnow()
        db.commit()
        db.refresh(progress)
        
        return progress
    
    # ==================== Leaderboard ====================
    
    def update_leaderboard(self, db: Session, cohort_id: str) -> Optional[CohortLeaderboard]:
        """Update cohort leaderboard with latest progress"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort or not cohort.leaderboard:
            return None
        
        if not cohort.leaderboard_enabled:
            return cohort.leaderboard
        
        members = self.get_cohort_members(db, cohort_id)
        
        # Calculate rankings based on progress percentage
        rankings = []
        for member in members:
            rankings.append({
                "user_id": member["user_id"],
                "username": member["username"],
                "avatar_url": member["avatar_url"],
                "progress_percentage": member["progress_percentage"],
                "completed_courses": member["completed_courses"],
                "total_courses": member["total_courses"],
                "last_active": member["last_active"].isoformat() if member["last_active"] else None
            })
        
        # Sort by progress percentage (highest first)
        rankings.sort(key=lambda x: x["progress_percentage"], reverse=True)
        
        # Add rank numbers
        for i, rank in enumerate(rankings, 1):
            rank["rank"] = i
        
        cohort.leaderboard.rankings = rankings
        cohort.leaderboard.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(cohort.leaderboard)
        
        logger.info(f"Leaderboard updated for cohort {cohort_id}")
        return cohort.leaderboard
    
    def get_leaderboard(self, db: Session, cohort_id: str, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Get cohort leaderboard, optionally refreshing"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort or not cohort.leaderboard:
            return None
        
        if not cohort.leaderboard_enabled:
            return []
        
        # Refresh if older than 1 hour or forced
        if force_refresh or not cohort.leaderboard.last_updated or \
           (datetime.utcnow() - cohort.leaderboard.last_updated) > timedelta(hours=1):
            self.update_leaderboard(db, cohort_id)
        
        return cohort.leaderboard.rankings
    
    def get_user_rank(self, db: Session, cohort_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user's rank in a cohort"""
        leaderboard = self.get_leaderboard(db, cohort_id)
        if not leaderboard:
            return None
        
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                return entry
        
        return None
    
    # ==================== Statistics ====================
    
    def get_cohort_statistics(self, db: Session, cohort_id: str) -> Dict[str, Any]:
        """Get statistics for a cohort"""
        cohort = self.get_cohort(db, cohort_id)
        if not cohort:
            return {}
        
        members = self.get_cohort_members(db, cohort_id)
        
        # Calculate overall statistics
        total_members = len(members)
        if total_members == 0:
            return {
                "total_members": 0,
                "average_progress": 0,
                "completed_count": 0,
                "active_today": 0,
                "active_week": 0
            }
        
        avg_progress = sum(m["progress_percentage"] for m in members) / total_members
        completed_count = sum(1 for m in members if m["progress_percentage"] == 100)
        
        # Active users
        today = datetime.utcnow().date()
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        active_today = sum(1 for m in members if m["last_active"] and m["last_active"].date() == today)
        active_week = sum(1 for m in members if m["last_active"] and m["last_active"] >= week_ago)
        
        return {
            "total_members": total_members,
            "average_progress": round(avg_progress, 1),
            "completed_count": completed_count,
            "completion_rate": round(completed_count / total_members * 100, 1),
            "active_today": active_today,
            "active_week": active_week,
            "total_courses": len(cohort.courses)
        }
