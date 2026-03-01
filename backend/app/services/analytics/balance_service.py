"""
Balance Curve Service
Tracks deposits, withdrawals, and net balance
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class BalanceService:
    """Service for balance curve analysis"""
    
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
        self.trades = self._fetch_trades()
        logger.info(f"BalanceService initialized with {len(self.trades)} trades")
    
    def _fetch_trades(self) -> List:
        """Fetch trades for the user"""
        from app.models.trade import Trade
        return self.db.query(Trade).filter(
            Trade.user_id == self.user_id
        ).order_by(Trade.exit_time).all()
    
    def get_balance_curve(self, interval: str = 'daily') -> Dict[str, Any]:
        """
        Get balance curve data
        interval: 'daily', 'weekly', 'monthly'
        """
        if not self.trades:
            return self._empty_balance()
        
        # Group by date based on interval
        balance_data = defaultdict(lambda: {
            'deposits': 0,
            'withdrawals': 0,
            'trading_pl': 0,
            'net_balance': 0
        })
        
        # Process trades for P/L
        for trade in self.trades:
            if trade.exit_time and trade.profit_loss:
                date = self._group_date(trade.exit_time, interval)
                balance_data[date]['trading_pl'] += trade.profit_loss
        
        # For demo purposes, add some sample deposits/withdrawals
        # In production, these would come from a separate table
        self._add_sample_balance_events(balance_data, interval)
        
        # Calculate running net balance
        result = []
        running_balance = 10000  # Starting balance of $10,000
        
        for date in sorted(balance_data.keys()):
            data = balance_data[date]
            running_balance += data['deposits']
            running_balance -= data['withdrawals']
            running_balance += data['trading_pl']
            data['net_balance'] = running_balance
            
            result.append({
                'date': date,
                'deposits': data['deposits'],
                'withdrawals': data['withdrawals'],
                'trading_pl': round(data['trading_pl'], 2),
                'net_balance': round(running_balance, 2)
            })
        
        return {
            'interval': interval,
            'data': result,
            'total_deposits': sum(d['deposits'] for d in result),
            'total_withdrawals': sum(d['withdrawals'] for d in result),
            'total_trading_pl': sum(d['trading_pl'] for d in result),
            'final_balance': running_balance
        }
    
    def get_comparison(self, interval: str = 'month') -> Dict[str, Any]:
        """
        Compare this period vs last period
        interval: 'month', 'week'
        """
        current_data = self.get_balance_curve(interval)
        
        # Get previous period data (simplified)
        # In production, you'd filter by date range
        previous_data = self.get_balance_curve(interval)
        
        # Calculate changes
        current_total = current_data['final_balance']
        previous_total = previous_data['final_balance'] * 0.95  # Simulated 5% less
        
        return {
            'current_period': current_data,
            'previous_period': previous_data,
            'change': {
                'absolute': round(current_total - previous_total, 2),
                'percentage': round((current_total / previous_total - 1) * 100, 2)
            }
        }
    
    def _group_date(self, date: datetime, interval: str) -> str:
        """Group date by interval"""
        if interval == 'daily':
            return date.strftime('%Y-%m-%d')
        elif interval == 'weekly':
            # Return week start date
            week_start = date - timedelta(days=date.weekday())
            return week_start.strftime('%Y-%m-%d')
        elif interval == 'monthly':
            return date.strftime('%Y-%m')
        else:
            return date.strftime('%Y-%m-%d')
    
    def _add_sample_balance_events(self, balance_data: Dict, interval: str):
        """Add sample deposit/withdrawal events (for demo)"""
        # In production, this would come from a database table
        import random
        
        dates = sorted(balance_data.keys())
        if not dates:
            return
        
        # Add random deposits every few periods
        for i, date in enumerate(dates):
            if i % 3 == 0:  # Every 3rd period
                balance_data[date]['deposits'] = random.randint(1000, 5000)
            if i % 5 == 0:  # Every 5th period
                balance_data[date]['withdrawals'] = random.randint(500, 2000)
    
    def _empty_balance(self) -> Dict:
        return {
            'interval': 'daily',
            'data': [],
            'total_deposits': 0,
            'total_withdrawals': 0,
            'total_trading_pl': 0,
            'final_balance': 0
        }
