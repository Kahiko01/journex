from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.services.trading_plan_service import TradingPlanService
import traceback

router = APIRouter(prefix="/trading-plan", tags=["trading-plan"])

# ========== Plan Endpoints ==========

@router.post("/plans")
async def create_plan(
    name: str,
    description: str,
    settings: Optional[dict] = None,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Create a new trading plan"""
    try:
        service = TradingPlanService(db, user_id)
        plan = service.create_plan(name, description, settings)
        return plan
    except Exception as e:
        print(f"Error creating plan: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_plans(
    active_only: bool = True,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get all user's trading plans"""
    try:
        service = TradingPlanService(db, user_id)
        plans = service.get_plans(active_only)
        return {"plans": plans}
    except Exception as e:
        print(f"Error getting plans: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans/{plan_id}")
async def get_plan(
    plan_id: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get a specific plan with its rules"""
    try:
        service = TradingPlanService(db, user_id)
        plan = service.get_plan(plan_id)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error getting plan: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: str,
    updates: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Update a trading plan"""
    try:
        service = TradingPlanService(db, user_id)
        plan = service.update_plan(plan_id, **updates)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error updating plan: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Delete a trading plan"""
    try:
        service = TradingPlanService(db, user_id)
        success = service.delete_plan(plan_id)
        if success:
            return {"message": "Plan deleted"}
        else:
            raise HTTPException(status_code=404, detail="Plan not found")
    except Exception as e:
        print(f"Error deleting plan: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ========== Rule Endpoints ==========

@router.post("/rules")
async def add_rule(
    plan_id: str,
    rule_data: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Add a rule to a plan"""
    try:
        service = TradingPlanService(db, user_id)
        rule = service.add_rule(plan_id, rule_data)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error adding rule: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
async def get_rules(
    plan_id: Optional[str] = None,
    rule_type: Optional[str] = None,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get all rules"""
    try:
        service = TradingPlanService(db, user_id)
        rules = service.get_rules(plan_id, rule_type)
        return {"rules": rules}
    except Exception as e:
        print(f"Error getting rules: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: str,
    rule_data: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Update a rule"""
    try:
        service = TradingPlanService(db, user_id)
        rule = service.update_rule(rule_id, rule_data)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error updating rule: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Delete a rule"""
    try:
        service = TradingPlanService(db, user_id)
        success = service.delete_rule(rule_id)
        if success:
            return {"message": "Rule deleted"}
        else:
            raise HTTPException(status_code=404, detail="Rule not found")
    except Exception as e:
        print(f"Error deleting rule: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ========== Violation Endpoints ==========

@router.post("/check-trade")
async def check_trade_violations(
    trade: dict,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Check a trade against all rules"""
    try:
        service = TradingPlanService(db, user_id)
        violations = service.check_trade_violations(trade)
        return {"violations": violations}
    except Exception as e:
        print(f"Error checking trade: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/violations")
async def get_violations(
    days: int = Query(30),
    plan_id: Optional[str] = None,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get recent rule violations"""
    try:
        service = TradingPlanService(db, user_id)
        violations = service.get_violations(days, plan_id)
        return {"violations": violations}
    except Exception as e:
        print(f"Error getting violations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ========== Weekly Review Endpoints ==========

@router.post("/weekly-review/{plan_id}")
async def generate_weekly_review(
    plan_id: str,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Generate a weekly review for a plan"""
    try:
        service = TradingPlanService(db, user_id)
        review = service.generate_weekly_review(plan_id)
        return review
    except Exception as e:
        print(f"Error generating review: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-reviews/{plan_id}")
async def get_weekly_reviews(
    plan_id: str,
    limit: int = Query(10),
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get weekly reviews for a plan"""
    try:
        service = TradingPlanService(db, user_id)
        reviews = service.get_weekly_reviews(plan_id, limit)
        return {"reviews": reviews}
    except Exception as e:
        print(f"Error getting reviews: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
