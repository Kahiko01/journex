from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.trade import Trade
import numpy as np
from collections import defaultdict

class ComparisonService:
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
        self.trades = self._fetch_trades()
    
    def _fetch_trades(self) -> List[Trade]:
        return self.db.query(Trade).filter(
            Trade.user_id == self.user_id
        ).order_by(Trade.exit_time).all()
    
    def get_comparison(self, comparison_type: str) -> Dict[str, Any]:
        if comparison_type == "strategy":
            return self._compare_strategies()
        elif comparison_type == "month":
            return self._compare_months()
        elif comparison_type == "year":
            return self._compare_years()
        elif comparison_type == "session":
            return self._compare_sessions()
        else:
            return {}
    
    def _compare_strategies(self) -> Dict[str, Any]:
        """Compare performance across strategies"""
        strategies = defaultdict(lambda: {"trades": 0, "wins": 0, "total_pl": 0})
        
        for trade in self.trades:
            if trade.strategy:
                s = strategies[trade.strategy]
                s["trades"] += 1
                if trade.profit_loss and trade.profit_loss > 0:
                    s["wins"] += 1
                if trade.profit_loss:
                    s["total_pl"] += trade.profit_loss
        
        result = []
        for name, data in strategies.items():
            result.append({
                "strategy": name,
                "trades": data["trades"],
                "win_rate": round(data["wins"] / data["trades"] * 100, 2) if data["trades"] > 0 else 0,
                "total_pl": round(data["total_pl"], 2)
            })
        
        return {"strategies": sorted(result, key=lambda x: x["total_pl"], reverse=True)}
    
    def _compare_months(self) -> Dict[str, Any]:
        """Compare month-over-month performance"""
        monthly = defaultdict(lambda: {"trades": 0, "wins": 0, "total_pl": 0})
        
        for trade in self.trades:
            if trade.exit_time:
                month_key = trade.exit_time.strftime("%Y-%m")
                m = monthly[month_key]
                m["trades"] += 1
                if trade.profit_loss and trade.profit_loss > 0:
                    m["wins"] += 1
                if trade.profit_loss:
                    m["total_pl"] += trade.profit_loss
        
        result = []
        for month, data in sorted(monthly.items()):
            result.append({
                "month": month,
                "trades": data["trades"],
                "win_rate": round(data["wins"] / data["trades"] * 100, 2) if data["trades"] > 0 else 0,
                "total_pl": round(data["total_pl"], 2)
            })
        
        return {"months": result}
    
    def _compare_sessions(self) -> Dict[str, Any]:
        """Compare performance across trading sessions"""
        sessions = {
            "asia": {"name": "Asia (00:00-08:00)", "trades": 0, "wins": 0, "total_pl": 0},
            "london": {"name": "London (08:00-16:00)", "trades": 0, "wins": 0, "total_pl": 0},
            "ny": {"name": "New York (16:00-00:00)", "trades": 0, "wins": 0, "total_pl": 0}
        }
        
        for trade in self.trades:
            if trade.exit_time:
                hour = trade.exit_time.hour
                if 0 <= hour < 8:
                    session = "asia"
                elif 8 <= hour < 16:
                    session = "london"
                else:
                    session = "ny"
                
                sessions[session]["trades"] += 1
                if trade.profit_loss and trade.profit_loss > 0:
                    sessions[session]["wins"] += 1
                if trade.profit_loss:
                    sessions[session]["total_pl"] += trade.profit_loss
        
        result = []
        for session, data in sessions.items():
            result.append({
                "name": data["name"],
                "trades": data["trades"],
                "win_rate": round(data["wins"] / data["trades"] * 100, 2) if data["trades"] > 0 else 0,
                "total_pl": round(data["total_pl"], 2)
            })
        
        return {"sessions": result}
