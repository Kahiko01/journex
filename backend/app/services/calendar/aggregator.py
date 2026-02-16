from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from app.models.daily_summary import DailySummary
from app.models.rule_violations import RuleViolation

class CalendarAggregator:
    @staticmethod
    def aggregate_daily_summary(user_id: int, trades: List[Dict], date: datetime) -> Dict[str, Any]:
        """Aggregate daily trading data into summary"""
        day_trades = [t for t in trades if t.get('exit_time') and 
                     datetime.fromisoformat(t['exit_time'].replace('Z', '+00:00')).date() == date.date()]
        
        if not day_trades:
            return None
        
        # Calculate P/L for each trade
        for trade in day_trades:
            if trade['direction'] == 'long':
                pl = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
            else:
                pl = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
            trade['profit_loss'] = pl
        
        winning_trades = [t for t in day_trades if t['profit_loss'] > 0]
        losing_trades = [t for t in day_trades if t['profit_loss'] < 0]
        
        # Session breakdown
        sessions = {'asia': {'trades': 0, 'pl': 0}, 
                   'london': {'trades': 0, 'pl': 0}, 
                   'ny': {'trades': 0, 'pl': 0}}
        
        for trade in day_trades:
            trade_time = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
            hour = trade_time.hour
            
            if 0 <= hour < 8:
                sessions['asia']['trades'] += 1
                sessions['asia']['pl'] += trade['profit_loss']
            elif 8 <= hour < 16:
                sessions['london']['trades'] += 1
                sessions['london']['pl'] += trade['profit_loss']
            else:
                sessions['ny']['trades'] += 1
                sessions['ny']['pl'] += trade['profit_loss']
        
        # Strategy performance
        strategy_perf = defaultdict(lambda: {'trades': 0, 'pl': 0, 'wins': 0})
        for trade in day_trades:
            strategy = trade.get('strategy', 'Unknown')
            strategy_perf[strategy]['trades'] += 1
            strategy_perf[strategy]['pl'] += trade['profit_loss']
            if trade['profit_loss'] > 0:
                strategy_perf[strategy]['wins'] += 1
        
        # Emotion tracking
        emotions = defaultdict(int)
        for trade in day_trades:
            if trade.get('emotion'):
                emotions[trade['emotion']] += 1
        
        # Calculate average R:R safely
        rr_values = []
        for trade in day_trades:
            if trade.get('stop_loss'):
                risk = abs(trade['stop_loss'] - trade['entry_price']) * trade['lot_size']
                if risk > 0:
                    rr = abs(trade['profit_loss'] / risk)
                    rr_values.append(rr)
        
        avg_rr = np.mean(rr_values) if rr_values else 0
        
        return {
            'user_id': user_id,
            'trade_date': date,
            'total_pl': sum(t['profit_loss'] for t in day_trades),
            'total_trades': len(day_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(day_trades) * 100) if day_trades else 0,
            'total_risk_taken': sum(abs(t.get('stop_loss', 0) - t['entry_price']) * t['lot_size'] for t in day_trades if t.get('stop_loss')),
            'sum_r_multiple': sum(t.get('r_multiple', 0) for t in day_trades),
            'avg_r_multiple': np.mean([t.get('r_multiple', 0) for t in day_trades]) if day_trades else 0,
            'largest_win': max((t['profit_loss'] for t in winning_trades), default=0),
            'largest_loss': min((t['profit_loss'] for t in losing_trades), default=0),
            'avg_rr': avg_rr,
            'asia_trades': sessions['asia']['trades'],
            'asia_pl': sessions['asia']['pl'],
            'london_trades': sessions['london']['trades'],
            'london_pl': sessions['london']['pl'],
            'ny_trades': sessions['ny']['trades'],
            'ny_pl': sessions['ny']['pl'],
            'strategy_performance': dict(strategy_perf),
            'emotions': dict(emotions),
            'high_rated_trades': len([t for t in day_trades if t.get('rating', 0) >= 4]),
            'discipline_score': 100  # Placeholder
        }
    
    @staticmethod
    def detect_overtrading(trades: List[Dict], daily_limit: int = 10) -> bool:
        """Detect if user is overtrading"""
        return len(trades) > daily_limit
    
    @staticmethod
    def detect_revenge_trading(trades: List[Dict]) -> bool:
        """Detect revenge trading pattern (bigger trades after losses)"""
        if len(trades) < 3:
            return False
        
        consecutive_losses = 0
        for i, trade in enumerate(trades):
            if trade.get('profit_loss', 0) < 0:
                consecutive_losses += 1
                if consecutive_losses >= 2 and i < len(trades) - 1:
                    next_trade = trades[i + 1]
                    if next_trade.get('lot_size', 0) > trade.get('lot_size', 0) * 1.5:
                        return True
            else:
                consecutive_losses = 0
        return False
    
    @staticmethod
    def calculate_risk_consistency(trades: List[Dict]) -> float:
        """Calculate risk consistency score (0-100)"""
        if len(trades) < 3:
            return 100
        
        risk_percentages = [t.get('risk_percent', 1) for t in trades if t.get('risk_percent')]
        if not risk_percentages:
            return 100
        
        std_dev = np.std(risk_percentages)
        mean_risk = np.mean(risk_percentages)
        cv = std_dev / mean_risk if mean_risk > 0 else 0
        
        # Lower CV means more consistent
        return max(0, min(100, 100 - (cv * 50)))
