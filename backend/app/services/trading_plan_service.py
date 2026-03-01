"""
Trading Plan Service for Rule Management and Violation Tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.trading_plan import TradingPlan, TradingRule, RuleViolation, WeeklyReview

logger = logging.getLogger(__name__)

class TradingPlanService:
    """Service for managing trading plans and rules"""
    
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
    
    # ========== Plan Management ==========
    
    def create_plan(self, name: str, description: str, settings: Dict = None) -> Dict[str, Any]:
        """Create a new trading plan"""
        plan = TradingPlan(
            user_id=self.user_id,
            name=name,
            description=description,
            tags=settings.get('tags', []) if settings else [],
            risk_percentage=settings.get('risk_percentage', 1.0) if settings else 1.0,
            max_daily_loss=settings.get('max_daily_loss') if settings else None,
            max_weekly_loss=settings.get('max_weekly_loss') if settings else None,
            max_positions=settings.get('max_positions', 1) if settings else 1
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return self._plan_to_dict(plan)
    
    def get_plans(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all user's trading plans"""
        query = self.db.query(TradingPlan).filter(TradingPlan.user_id == self.user_id)
        
        if active_only:
            query = query.filter(TradingPlan.is_active == True)
        
        plans = query.order_by(TradingPlan.created_at.desc()).all()
        return [self._plan_to_dict(p) for p in plans]
    
    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get a specific plan with its rules"""
        plan = self.db.query(TradingPlan).filter(
            TradingPlan.id == plan_id,
            TradingPlan.user_id == self.user_id
        ).first()
        
        if not plan:
            raise ValueError("Plan not found")
        
        # Get rules for this plan
        rules = self.db.query(TradingRule).filter(
            TradingRule.plan_id == plan_id,
            TradingRule.is_active == True
        ).all()
        
        plan_dict = self._plan_to_dict(plan)
        plan_dict['rules'] = [self._rule_to_dict(r) for r in rules]
        
        return plan_dict
    
    def update_plan(self, plan_id: str, **kwargs) -> Dict[str, Any]:
        """Update a trading plan"""
        plan = self.db.query(TradingPlan).filter(
            TradingPlan.id == plan_id,
            TradingPlan.user_id == self.user_id
        ).first()
        
        if not plan:
            raise ValueError("Plan not found")
        
        for key, value in kwargs.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        
        self.db.commit()
        self.db.refresh(plan)
        
        return self._plan_to_dict(plan)
    
    def delete_plan(self, plan_id: str) -> bool:
        """Soft delete a plan"""
        plan = self.db.query(TradingPlan).filter(
            TradingPlan.id == plan_id,
            TradingPlan.user_id == self.user_id
        ).first()
        
        if not plan:
            return False
        
        plan.is_active = False
        self.db.commit()
        
        return True
    
    # ========== Rule Management ==========
    
    def add_rule(self, plan_id: str, rule_data: Dict) -> Dict[str, Any]:
        """Add a rule to a plan"""
        # Verify plan exists
        plan = self.db.query(TradingPlan).filter(
            TradingPlan.id == plan_id,
            TradingPlan.user_id == self.user_id
        ).first()
        
        if not plan:
            raise ValueError("Plan not found")
        
        rule = TradingRule(
            plan_id=plan_id,
            user_id=self.user_id,
            name=rule_data['name'],
            description=rule_data.get('description', ''),
            rule_type=rule_data['rule_type'],
            conditions=rule_data['conditions'],
            is_required=rule_data.get('is_required', True),
            penalty_score=rule_data.get('penalty_score', 10)
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return self._rule_to_dict(rule)
    
    def update_rule(self, rule_id: str, rule_data: Dict) -> Dict[str, Any]:
        """Update a rule"""
        rule = self.db.query(TradingRule).filter(
            TradingRule.id == rule_id,
            TradingRule.user_id == self.user_id
        ).first()
        
        if not rule:
            raise ValueError("Rule not found")
        
        for key, value in rule_data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.db.commit()
        self.db.refresh(rule)
        
        return self._rule_to_dict(rule)
    
    def delete_rule(self, rule_id: str) -> bool:
        """Soft delete a rule"""
        rule = self.db.query(TradingRule).filter(
            TradingRule.id == rule_id,
            TradingRule.user_id == self.user_id
        ).first()
        
        if not rule:
            return False
        
        rule.is_active = False
        self.db.commit()
        
        return True
    
    def get_rules(self, plan_id: Optional[str] = None, rule_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all rules, optionally filtered"""
        query = self.db.query(TradingRule).filter(
            TradingRule.user_id == self.user_id,
            TradingRule.is_active == True
        )
        
        if plan_id:
            query = query.filter(TradingRule.plan_id == plan_id)
        
        if rule_type:
            query = query.filter(TradingRule.rule_type == rule_type)
        
        rules = query.order_by(TradingRule.created_at).all()
        return [self._rule_to_dict(r) for r in rules]
    
    # ========== Violation Tracking ==========
    
    def check_trade_violations(self, trade: Dict) -> List[Dict]:
        """Check a trade against all active rules"""
        violations = []
        
        # Get all active rules
        rules = self.db.query(TradingRule).filter(
            TradingRule.user_id == self.user_id,
            TradingRule.is_active == True
        ).all()
        
        for rule in rules:
            violation = self._evaluate_rule(rule, trade)
            if violation:
                # Log the violation
                v = RuleViolation(
                    user_id=self.user_id,
                    rule_id=rule.id,
                    trade_id=trade.get('id'),
                    rule_name=rule.name,
                    rule_type=rule.rule_type,
                    description=violation['description'],
                    severity=violation.get('severity', 'medium'),
                    expected_value=violation.get('expected'),
                    actual_value=violation.get('actual'),
                    trade_data=trade
                )
                self.db.add(v)
                violations.append(violation)
        
        if violations:
            self.db.commit()
        
        return violations
    
    def get_violations(self, days: int = 30, plan_id: Optional[str] = None) -> List[Dict]:
        """Get recent rule violations"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(RuleViolation).filter(
            RuleViolation.user_id == self.user_id,
            RuleViolation.violation_date >= start_date
        )
        
        if plan_id:
            query = query.join(TradingRule).filter(TradingRule.plan_id == plan_id)
        
        violations = query.order_by(RuleViolation.violation_date.desc()).all()
        
        return [{
            'id': str(v.id),
            'rule_name': v.rule_name,
            'rule_type': v.rule_type,
            'description': v.description,
            'severity': v.severity,
            'date': v.violation_date.isoformat(),
            'trade_id': v.trade_id,
            'is_reviewed': v.is_reviewed
        } for v in violations]
    
    # ========== Weekly Reviews ==========
    
    def generate_weekly_review(self, plan_id: str) -> Dict[str, Any]:
        """Generate a weekly review for a plan"""
        # Calculate week boundaries (Monday to Sunday)
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        # Get violations for this week
        violations = self.db.query(RuleViolation).filter(
            RuleViolation.user_id == self.user_id,
            RuleViolation.violation_date >= week_start,
            RuleViolation.violation_date < week_end
        ).all()
        
        # Get trades for this week (simplified - would join with trades table)
        # This is a placeholder - you'd integrate with your trades data
        
        # Calculate statistics
        total_violations = len(violations)
        violations_by_type = {}
        for v in violations:
            violations_by_type[v.rule_type] = violations_by_type.get(v.rule_type, 0) + 1
        
        # Calculate adherence rate (placeholder)
        adherence_rate = max(0, 100 - (total_violations * 5))
        
        # Create review
        review = WeeklyReview(
            user_id=self.user_id,
            plan_id=plan_id,
            week_start=week_start,
            week_end=week_end,
            total_trades=0,  # Would calculate from trades
            violations_count=total_violations,
            adherence_rate=adherence_rate,
            discipline_score=int(adherence_rate),
            rule_stats=violations_by_type
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        return {
            'id': str(review.id),
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'violations': total_violations,
            'adherence_rate': adherence_rate,
            'discipline_score': review.discipline_score,
            'by_type': violations_by_type
        }
    
    def get_weekly_reviews(self, plan_id: str, limit: int = 10) -> List[Dict]:
        """Get weekly reviews for a plan"""
        reviews = self.db.query(WeeklyReview).filter(
            WeeklyReview.user_id == self.user_id,
            WeeklyReview.plan_id == plan_id
        ).order_by(WeeklyReview.week_start.desc()).limit(limit).all()
        
        return [{
            'id': str(r.id),
            'week_start': r.week_start.isoformat(),
            'week_end': r.week_end.isoformat(),
            'violations': r.violations_count,
            'adherence_rate': r.adherence_rate,
            'discipline_score': r.discipline_score
        } for r in reviews]
    
    # ========== Helper Methods ==========
    
    def _evaluate_rule(self, rule: TradingRule, trade: Dict) -> Optional[Dict]:
        """Evaluate a rule against a trade"""
        conditions = rule.conditions
        rule_type = conditions.get('type')
        
        if rule_type == 'max_risk':
            # Check risk percentage
            risk = trade.get('risk_percent', 0)
            max_risk = conditions.get('value', 2.0)
            if risk > max_risk:
                return {
                    'description': f"Risk {risk}% exceeds maximum {max_risk}%",
                    'severity': 'high',
                    'expected': max_risk,
                    'actual': risk
                }
        
        elif rule_type == 'min_rr':
            # Check risk-reward ratio
            rr = trade.get('risk_reward', 0)
            min_rr = conditions.get('value', 1.5)
            if rr < min_rr:
                return {
                    'description': f"Risk-reward {rr} below minimum {min_rr}",
                    'severity': 'medium',
                    'expected': min_rr,
                    'actual': rr
                }
        
        elif rule_type == 'session_restriction':
            # Check trading session
            session = trade.get('session', '')
            allowed = conditions.get('allowed_sessions', [])
            if session and session not in allowed:
                return {
                    'description': f"Trading in {session} session not allowed",
                    'severity': 'medium',
                    'expected': allowed,
                    'actual': session
                }
        
        elif rule_type == 'max_daily_trades':
            # This would need aggregation - placeholder
            pass
        
        return None
    
    def _plan_to_dict(self, plan: TradingPlan) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            'id': str(plan.id),
            'name': plan.name,
            'description': plan.description,
            'is_active': plan.is_active,
            'tags': plan.tags,
            'risk_percentage': plan.risk_percentage,
            'max_daily_loss': plan.max_daily_loss,
            'max_weekly_loss': plan.max_weekly_loss,
            'max_positions': plan.max_positions,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat() if plan.updated_at else None
        }
    
    def _rule_to_dict(self, rule: TradingRule) -> Dict[str, Any]:
        """Convert rule to dictionary"""
        return {
            'id': str(rule.id),
            'plan_id': str(rule.plan_id),
            'name': rule.name,
            'description': rule.description,
            'rule_type': rule.rule_type,
            'conditions': rule.conditions,
            'is_required': rule.is_required,
            'penalty_score': rule.penalty_score,
            'is_active': rule.is_active,
            'created_at': rule.created_at.isoformat()
        }
