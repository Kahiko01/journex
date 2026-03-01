"""
Checklist Service for Trading Preparation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy.orm import Session
from app.models.checklist import ChecklistTemplate, UserChecklist, ChecklistCompletion, ChecklistAnalytics

logger = logging.getLogger(__name__)

class ChecklistService:
    """Service for managing trading checklists"""
    
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
    
    # ========== Template Management ==========
    
    def get_default_templates(self) -> List[Dict[str, Any]]:
        """Get all default checklist templates"""
        templates = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.is_default == True
        ).all()
        
        return [self._template_to_dict(t) for t in templates]
    
    def create_from_template(self, template_id: str, custom_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a user checklist from a template"""
        template = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.id == template_id
        ).first()
        
        if not template:
            raise ValueError("Template not found")
        
        user_checklist = UserChecklist(
            user_id=self.user_id,
            name=custom_name or template.name,
            description=template.description,
            checklist_type=template.category,
            items=template.items  # Copy template items
        )
        
        self.db.add(user_checklist)
        self.db.commit()
        self.db.refresh(user_checklist)
        
        return self._user_checklist_to_dict(user_checklist)
    
    # ========== User Checklist Management ==========
    
    def get_user_checklists(self, checklist_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all user checklists"""
        query = self.db.query(UserChecklist).filter(
            UserChecklist.user_id == self.user_id,
            UserChecklist.is_active == True
        )
        
        if checklist_type:
            query = query.filter(UserChecklist.checklist_type == checklist_type)
        
        checklists = query.order_by(UserChecklist.created_at).all()
        return [self._user_checklist_to_dict(c) for c in checklists]
    
    def create_checklist(self, name: str, description: str, checklist_type: str, items: List[Dict]) -> Dict[str, Any]:
        """Create a custom checklist"""
        # Validate items
        for i, item in enumerate(items):
            if 'text' not in item:
                item['text'] = f"Item {i+1}"
            if 'required' not in item:
                item['required'] = True
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())
            if 'order' not in item:
                item['order'] = i
        
        checklist = UserChecklist(
            user_id=self.user_id,
            name=name,
            description=description,
            checklist_type=checklist_type,
            items=items
        )
        
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        
        return self._user_checklist_to_dict(checklist)
    
    def update_checklist(self, checklist_id: str, **kwargs) -> Dict[str, Any]:
        """Update a checklist"""
        checklist = self.db.query(UserChecklist).filter(
            UserChecklist.id == checklist_id,
            UserChecklist.user_id == self.user_id
        ).first()
        
        if not checklist:
            raise ValueError("Checklist not found")
        
        for key, value in kwargs.items():
            if hasattr(checklist, key):
                setattr(checklist, key, value)
        
        self.db.commit()
        self.db.refresh(checklist)
        
        return self._user_checklist_to_dict(checklist)
    
    def delete_checklist(self, checklist_id: str) -> bool:
        """Delete a checklist"""
        checklist = self.db.query(UserChecklist).filter(
            UserChecklist.id == checklist_id,
            UserChecklist.user_id == self.user_id
        ).first()
        
        if not checklist:
            return False
        
        # Soft delete
        checklist.is_active = False
        self.db.commit()
        
        return True
    
    # ========== Checklist Completion ==========
    
    def complete_checklist(self, checklist_id: str, completion_data: Dict, trade_id: Optional[int] = None) -> Dict[str, Any]:
        """Mark a checklist as completed for a trade"""
        checklist = self.db.query(UserChecklist).filter(
            UserChecklist.id == checklist_id,
            UserChecklist.user_id == self.user_id
        ).first()
        
        if not checklist:
            raise ValueError("Checklist not found")
        
        # Calculate completion percentage
        items = checklist.items
        total_items = len(items)
        completed_items = sum(1 for item in items if completion_data.get(item.get('id'), False))
        completion_pct = (completed_items / total_items * 100) if total_items > 0 else 0
        
        completion = ChecklistCompletion(
            user_id=self.user_id,
            checklist_id=checklist_id,
            trade_id=trade_id,
            completion_data=completion_data,
            completion_percentage=completion_pct
        )
        
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        
        # Update analytics
        self._update_analytics(checklist.checklist_type, completion_pct)
        
        return {
            'id': str(completion.id),
            'checklist_id': str(checklist_id),
            'completion_percentage': completion_pct,
            'completed_at': completion.completed_at.isoformat(),
            'trade_id': trade_id
        }
    
    def get_checklist_history(self, checklist_id: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get checklist completion history"""
        query = self.db.query(ChecklistCompletion).filter(
            ChecklistCompletion.user_id == self.user_id,
            ChecklistCompletion.completed_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if checklist_id:
            query = query.filter(ChecklistCompletion.checklist_id == checklist_id)
        
        completions = query.order_by(ChecklistCompletion.completed_at.desc()).all()
        
        return [{
            'id': str(c.id),
            'checklist_id': str(c.checklist_id),
            'trade_id': c.trade_id,
            'completion_percentage': c.completion_percentage,
            'completed_at': c.completed_at.isoformat()
        } for c in completions]
    
    # ========== Analytics ==========
    
    def get_adherence_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get checklist adherence analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        completions = self.db.query(ChecklistCompletion).filter(
            ChecklistCompletion.user_id == self.user_id,
            ChecklistCompletion.completed_at >= start_date
        ).all()
        
        if not completions:
            return {
                'total_completions': 0,
                'avg_completion_rate': 0,
                'by_type': {},
                'trend': []
            }
        
        # Group by checklist type
        checklists = self.db.query(UserChecklist).filter(
            UserChecklist.user_id == self.user_id
        ).all()
        
        checklist_map = {str(c.id): c.checklist_type for c in checklists}
        
        by_type = {}
        for comp in completions:
            c_type = checklist_map.get(str(comp.checklist_id), 'unknown')
            if c_type not in by_type:
                by_type[c_type] = {'count': 0, 'avg_rate': 0, 'total_rate': 0}
            
            by_type[c_type]['count'] += 1
            by_type[c_type]['total_rate'] += comp.completion_percentage
        
        for c_type, data in by_type.items():
            data['avg_rate'] = data['total_rate'] / data['count']
        
        # Daily trend
        trend = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_completions = [c for c in completions 
                              if c.completed_at.date() == day.date()]
            
            if day_completions:
                avg = sum(c.completion_percentage for c in day_completions) / len(day_completions)
                trend.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'avg_rate': avg,
                    'count': len(day_completions)
                })
        
        return {
            'total_completions': len(completions),
            'avg_completion_rate': sum(c.completion_percentage for c in completions) / len(completions),
            'by_type': by_type,
            'trend': trend
        }
    
    # ========== Helper Methods ==========
    
    def _update_analytics(self, checklist_type: str, completion_rate: float):
        """Update analytics (simplified)"""
        # In production, you'd aggregate this properly
        analytics = ChecklistAnalytics(
            user_id=self.user_id,
            checklist_type=checklist_type,
            total_checks=1,
            completed_checks=1 if completion_rate == 100 else 0,
            adherence_rate=completion_rate,
            trades_with_checklist=1 if completion_rate > 0 else 0
        )
        
        self.db.add(analytics)
        self.db.commit()
    
    def _template_to_dict(self, template: ChecklistTemplate) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'id': str(template.id),
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'is_default': template.is_default,
            'items': template.items,
            'created_at': template.created_at.isoformat()
        }
    
    def _user_checklist_to_dict(self, checklist: UserChecklist) -> Dict[str, Any]:
        """Convert user checklist to dictionary"""
        return {
            'id': str(checklist.id),
            'name': checklist.name,
            'description': checklist.description,
            'type': checklist.checklist_type,
            'items': checklist.items,
            'is_active': checklist.is_active,
            'created_at': checklist.created_at.isoformat(),
            'updated_at': checklist.updated_at.isoformat() if checklist.updated_at else None
        }
