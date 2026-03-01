#!/usr/bin/env python3
"""
Migrate trades from in-memory storage to PostgreSQL
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.trade import Trade
from app.api.endpoints.trades import trades_db
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_trades():
    """Migrate all trades from trades_db to PostgreSQL"""
    logger.info(f"Starting migration of {len(trades_db)} trades...")
    
    db = SessionLocal()
    migrated = 0
    errors = 0
    
    try:
        for t in trades_db:
            try:
                # Parse dates if they exist
                entry_time = None
                exit_time = None
                
                if t.get('entry_time'):
                    try:
                        if isinstance(t['entry_time'], str):
                            entry_time = datetime.fromisoformat(t['entry_time'].replace('Z', '+00:00'))
                    except:
                        pass
                
                if t.get('exit_time'):
                    try:
                        if isinstance(t['exit_time'], str):
                            exit_time = datetime.fromisoformat(t['exit_time'].replace('Z', '+00:00'))
                    except:
                        pass
                
                # Create trade object
                trade = Trade(
                    user_id=t.get('user_id', 1),
                    symbol=t['symbol'],
                    direction=t['direction'],
                    entry_price=float(t['entry_price']),
                    exit_price=float(t['exit_price']) if t.get('exit_price') else None,
                    stop_loss=float(t['stop_loss']) if t.get('stop_loss') else None,
                    take_profit=float(t['take_profit']) if t.get('take_profit') else None,
                    lot_size=float(t['lot_size']),
                    strategy=t.get('strategy'),
                    emotion=t.get('emotion'),
                    rating=t.get('rating'),
                    profit_loss=float(t['profit_loss']) if t.get('profit_loss') else None,
                    r_multiple=float(t['r_multiple']) if t.get('r_multiple') else None,
                    entry_time=entry_time,
                    exit_time=exit_time
                )
                
                db.add(trade)
                migrated += 1
                
                if migrated % 10 == 0:
                    logger.info(f"Migrated {migrated} trades...")
                    
            except Exception as e:
                logger.error(f"Error migrating trade {t.get('id')}: {e}")
                errors += 1
        
        db.commit()
        logger.info(f"Migration complete! Migrated: {migrated}, Errors: {errors}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_trades()
