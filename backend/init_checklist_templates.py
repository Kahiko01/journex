#!/usr/bin/env python3
"""
Initialize default checklist templates in the database
"""

import sys
import uuid
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.checklist import ChecklistTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_templates():
    """Initialize default checklist templates"""
    db = SessionLocal()
    
    templates = [
        {
            'name': 'Pre-Trade Checklist',
            'description': 'Essential checks before entering any trade',
            'category': 'pre-trade',
            'is_default': True,
            'items': [
                {'text': 'Market structure confirmed', 'required': True, 'order': 1, 'id': str(uuid.uuid4())},
                {'text': 'Risk ≤ 2% of account', 'required': True, 'order': 2, 'id': str(uuid.uuid4())},
                {'text': 'Stop loss placed', 'required': True, 'order': 3, 'id': str(uuid.uuid4())},
                {'text': 'Take profit level identified', 'required': True, 'order': 4, 'id': str(uuid.uuid4())},
                {'text': 'News checked (no high-impact events)', 'required': True, 'order': 5, 'id': str(uuid.uuid4())},
                {'text': 'Entry rules confirmed', 'required': True, 'order': 6, 'id': str(uuid.uuid4())},
                {'text': 'Position size calculated', 'required': True, 'order': 7, 'id': str(uuid.uuid4())},
                {'text': 'Risk-reward ratio ≥ 1.5', 'required': False, 'order': 8, 'id': str(uuid.uuid4())},
                {'text': 'Multiple timeframe analysis done', 'required': False, 'order': 9, 'id': str(uuid.uuid4())}
            ]
        },
        {
            'name': 'Post-Trade Review',
            'description': 'Review questions after closing a trade',
            'category': 'post-trade',
            'is_default': True,
            'items': [
                {'text': 'Trade followed the plan', 'required': True, 'order': 1, 'id': str(uuid.uuid4())},
                {'text': 'Stop loss respected', 'required': True, 'order': 2, 'id': str(uuid.uuid4())},
                {'text': 'Emotion during trade recorded', 'required': True, 'order': 3, 'id': str(uuid.uuid4())},
                {'text': 'What went well?', 'required': False, 'order': 4, 'id': str(uuid.uuid4())},
                {'text': 'What could be improved?', 'required': False, 'order': 5, 'id': str(uuid.uuid4())},
                {'text': 'Screenshot saved', 'required': False, 'order': 6, 'id': str(uuid.uuid4())}
            ]
        },
        {
            'name': 'Daily Preparation',
            'description': 'Daily routine before trading session',
            'category': 'daily',
            'is_default': True,
            'items': [
                {'text': 'Overnight market review', 'required': True, 'order': 1, 'id': str(uuid.uuid4())},
                {'text': 'Economic calendar checked', 'required': True, 'order': 2, 'id': str(uuid.uuid4())},
                {'text': 'Key levels identified', 'required': True, 'order': 3, 'id': str(uuid.uuid4())},
                {'text': 'Trading plan for the day', 'required': True, 'order': 4, 'id': str(uuid.uuid4())},
                {'text': 'Risk limit set', 'required': True, 'order': 5, 'id': str(uuid.uuid4())},
                {'text': 'Journal ready', 'required': False, 'order': 6, 'id': str(uuid.uuid4())}
            ]
        },
        {
            'name': 'Weekly Review',
            'description': 'End of week performance review',
            'category': 'weekly',
            'is_default': True,
            'items': [
                {'text': 'Review all trades from the week', 'required': True, 'order': 1, 'id': str(uuid.uuid4())},
                {'text': 'Calculate win rate', 'required': True, 'order': 2, 'id': str(uuid.uuid4())},
                {'text': 'Identify patterns', 'required': True, 'order': 3, 'id': str(uuid.uuid4())},
                {'text': 'Plan for next week', 'required': True, 'order': 4, 'id': str(uuid.uuid4())},
                {'text': 'Update trading journal', 'required': True, 'order': 5, 'id': str(uuid.uuid4())},
                {'text': 'Review risk management', 'required': True, 'order': 6, 'id': str(uuid.uuid4())}
            ]
        }
    ]
    
    try:
        for template_data in templates:
            # Check if template already exists
            existing = db.query(ChecklistTemplate).filter(
                ChecklistTemplate.name == template_data['name']
            ).first()
            
            if not existing:
                template = ChecklistTemplate(**template_data)
                db.add(template)
                logger.info(f"Added template: {template_data['name']}")
            else:
                logger.info(f"Template already exists: {template_data['name']}")
        
        db.commit()
        logger.info("All templates initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing templates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_templates()
