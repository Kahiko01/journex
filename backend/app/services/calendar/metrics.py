from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np

class CalendarMetrics:
    @staticmethod
    def calculate_weekly_summary(daily_data: List[Dict]) -> Dict[str, Any]:
        """Calculate weekly performance summary"""
        if not daily_data:
            return {}
        
        total_pl = sum(d.get('total_pl', 0) for d in daily_data)
        total_trades = sum(d.get('total_trades', 0) for d in daily_data)
        winning_trades = sum(d.get('winning_trades', 0) for d in daily_data)
        
        # Calculate max drawdown for the week
        cumulative_pl = 0
        peak = 0
        max_drawdown = 0
        
        for day in sorted(daily_data, key=lambda x: x.get('trade_date', '')):
            cumulative_pl += day.get('total_pl', 0)
            if cumulative_pl > peak:
                peak = cumulative_pl
            drawdown = peak - cumulative_pl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Find most profitable strategy
        strategy_pl = {}
        for day in daily_data:
            for strategy, perf in day.get('strategy_performance', {}).items():
                strategy_pl[strategy] = strategy_pl.get(strategy, 0) + perf.get('pl', 0)
        
        best_strategy = max(strategy_pl.items(), key=lambda x: x[1]) if strategy_pl else ('None', 0)
        
        # Calculate risk consistency
        risk_scores = [d.get('discipline_score', 100) for d in daily_data if d.get('discipline_score')]
        avg_risk_score = np.mean(risk_scores) if risk_scores else 100
        
        return {
            'total_pl': round(total_pl, 2),
            'total_trades': total_trades,
            'win_rate': round((winning_trades / total_trades * 100) if total_trades > 0 else 0, 1),
            'avg_r': round(np.mean([d.get('avg_r_multiple', 0) for d in daily_data if d.get('avg_r_multiple')]), 2),
            'max_drawdown': round(max_drawdown, 2),
            'best_strategy': best_strategy[0],
            'best_strategy_pl': round(best_strategy[1], 2),
            'risk_consistency': round(avg_risk_score, 1)
        }
    
    @staticmethod
    def calculate_monthly_summary(weekly_data: List[Dict]) -> Dict[str, Any]:
        """Calculate monthly performance summary"""
        if not weekly_data:
            return {}
        
        return {
            'total_pl': sum(w.get('total_pl', 0) for w in weekly_data),
            'total_trades': sum(w.get('total_trades', 0) for w in weekly_data),
            'avg_win_rate': np.mean([w.get('win_rate', 0) for w in weekly_data]),
            'best_week': max(weekly_data, key=lambda x: x.get('total_pl', 0)) if weekly_data else {}
        }
    
    @staticmethod
    def calculate_discipline_score(daily_summary: Dict) -> int:
        """Calculate discipline score for a day (0-100)"""
        score = 100
        
        # Deduct for rule violations
        score -= daily_summary.get('rule_violations_count', 0) * 10
        
        # Deduct for overtrading
        if daily_summary.get('overtrading_detected', False):
            score -= 15
        
        # Deduct for revenge trading
        if daily_summary.get('revenge_trading_detected', False):
            score -= 20
        
        # Add for consistency
        if daily_summary.get('win_rate', 0) > 60:
            score += 5
        
        # Add for proper risk management
        if daily_summary.get('avg_rr', 0) > 1.5:
            score += 5
        
        return max(0, min(100, score))
