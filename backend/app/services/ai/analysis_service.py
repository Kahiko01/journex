"""
AI-Powered Trade Analysis Service
Uses Kimi 2.5 via NVIDIA API
"""

from app.services.ai.kimi_service import KimiService
import logging

logger = logging.getLogger(__name__)

class AITradeAnalysisService:
    def __init__(self):
        self.kimi = KimiService()
    
    def analyze_trade(self, trade_data: dict, user_history: list = None) -> dict:
        """Analyze a single trade"""
        return self.kimi.analyze_trade(trade_data, user_history)
    
    def batch_analyze_trades(self, trades: list) -> list:
        """Analyze multiple trades"""
        results = []
        for trade in trades:
            analysis = self.analyze_trade(trade)
            results.append({
                'trade_id': trade.get('id'),
                'analysis': analysis
            })
        return results
