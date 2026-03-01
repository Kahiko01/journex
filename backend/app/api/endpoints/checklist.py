from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.db.session import get_db
from app.services.checklist_service import ChecklistService
import traceback

router = APIRouter(prefix="/checklist", tags=["checklist"])

@router.get("/templates")
async def get_templates(db: Session = Depends(get_db)):
    """Get all default checklist templates"""
    try:
        service = ChecklistService(db, user_id=1)
        templates = service.get_default_templates()
        return {"templates": templates}
    except Exception as e:
        print(f"Error getting templates: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/create")
async def create_from_template(
    template_id: str,
    custom_name: Optional[str] = None,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Create a user checklist from a template"""
    try:
        service = ChecklistService(db, user_id)
        checklist = service.create_from_template(template_id, custom_name)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error creating from template: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user")
async def get_user_checklists(
    checklist_type: Optional[str] = None,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get user's checklists"""
    try:
        service = ChecklistService(db, user_id)
        checklists = service.get_user_checklists(checklist_type)
        return {"checklists": checklists}
    except Exception as e:
        print(f"Error getting user checklists: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user")
async def create_checklist(
    checklist_data: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Create a custom checklist"""
    try:
        service = ChecklistService(db, user_id)
        
        # Extract data from request body
        name = checklist_data.get('name')
        description = checklist_data.get('description')
        checklist_type = checklist_data.get('checklist_type')
        items = checklist_data.get('items', [])
        
        if not name or not checklist_type:
            raise HTTPException(status_code=400, detail="Name and type are required")
        
        checklist = service.create_checklist(name, description, checklist_type, items)
        return checklist
    except Exception as e:
        print(f"Error creating checklist: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user/{checklist_id}")
async def update_checklist(
    checklist_id: str,
    update_data: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Update a checklist"""
    try:
        service = ChecklistService(db, user_id)
        
        # Extract update data
        name = update_data.get('name')
        description = update_data.get('description')
        items = update_data.get('items')
        
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if description is not None:
            kwargs['description'] = description
        if items is not None:
            kwargs['items'] = items
        
        checklist = service.update_checklist(checklist_id, **kwargs)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error updating checklist: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{checklist_id}")
async def delete_checklist(
    checklist_id: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Delete a checklist"""
    try:
        service = ChecklistService(db, user_id)
        success = service.delete_checklist(checklist_id)
        if success:
            return {"message": "Checklist deleted"}
        else:
            raise HTTPException(status_code=404, detail="Checklist not found")
    except Exception as e:
        print(f"Error deleting checklist: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_checklist(
    completion_data: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Mark a checklist as completed"""
    try:
        service = ChecklistService(db, user_id)
        
        checklist_id = completion_data.get('checklist_id')
        data = completion_data.get('completion_data', {})
        trade_id = completion_data.get('trade_id')
        
        if not checklist_id:
            raise HTTPException(status_code=400, detail="checklist_id is required")
        
        result = service.complete_checklist(checklist_id, data, trade_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error completing checklist: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_checklist_history(
    checklist_id: Optional[str] = None,
    days: int = Query(30),
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get checklist completion history"""
    try:
        service = ChecklistService(db, user_id)
        history = service.get_checklist_history(checklist_id, days)
        return {"history": history}
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_checklist_analytics(
    days: int = Query(30),
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get checklist adherence analytics"""
    try:
        service = ChecklistService(db, user_id)
        analytics = service.get_adherence_analytics(days)
        return analytics
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
