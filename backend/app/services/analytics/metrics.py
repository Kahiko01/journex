from typing import List, Dict, Any
from .calculator import AnalyticsCalculator

class AnalyticsService:
    def __init__(self):
        self.calculator = AnalyticsCalculator()
    
    def get_dashboard_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Get all analytics metrics for dashboard"""
        return {
            "drawdown": self.calculator.calculate_drawdown(trades),
            "risk": self.calculator.calculate_risk_metrics(trades),
            "sessions": self.calculator.analyze_sessions(trades),
            "r_stats": self.calculator.calculate_r_multiple_stats(trades)
        }
