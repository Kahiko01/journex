"""
Performance Stability Metrics Service
Measures consistency and stability of trading performance
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from .formulas.mathematical_formulas import TradingFormulas

class StabilityMetricsService:
    
    def __init__(self):
        self.formulas = TradingFormulas()
    
    def analyze_stability(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive stability analysis
        """
        if len(trades) < 10:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Calculate various stability metrics
        rolling_metrics = self._calculate_rolling_metrics(trades)
        volatility_metrics = self._calculate_volatility_metrics(trades)
        consistency_index = self._calculate_consistency_index(trades)
        equity_smoothness = self._calculate_equity_smoothness(trades)
        stability_trend = self._analyze_stability_trend(trades)
        
        # Calculate stability score
        stability_score = self._calculate_stability_score(
            volatility_metrics,
            consistency_index,
            equity_smoothness
        )
        
        return {
            "rolling_metrics": rolling_metrics,
            "volatility_metrics": volatility_metrics,
            "consistency_index": consistency_index,
            "equity_smoothness": equity_smoothness,
            "stability_trend": stability_trend,
            "stability_score": stability_score,
            "stability_grade": self._get_stability_grade(stability_score),
            "comparison_to_benchmark": self._compare_to_benchmark(trades)
        }
    
    def _calculate_rolling_metrics(self, trades: List[Dict], window: int = 20) -> Dict[str, Any]:
        """Calculate rolling performance metrics"""
        if len(trades) < window:
            window = len(trades) // 2
        
        rolling_sharpe = []
        rolling_expectancy = []
        rolling_win_rate = []
        rolling_volatility = []
        dates = []
        
        for i in range(len(trades) - window + 1):
            window_trades = trades[i:i + window]
            returns = [t.get('profit_loss', 0) for t in window_trades]
            
            # Calculate metrics for this window
            sharpe = self.formulas.calculate_sharpe_ratio(returns)
            expectancy = self.formulas.calculate_expectancy(window_trades)
            win_rate = len([r for r in returns if r > 0]) / window * 100
            volatility = np.std(returns) if len(returns) > 1 else 0
            
            rolling_sharpe.append(sharpe)
            rolling_expectancy.append(expectancy)
            rolling_win_rate.append(round(win_rate, 2))
            rolling_volatility.append(round(volatility, 2))
            dates.append(trades[i + window - 1].get('exit_time', ''))
        
        # Calculate stability of rolling metrics
        if rolling_sharpe:
            sharpe_stability = 100 - min(100, np.std(rolling_sharpe) * 50)
            expectancy_stability = 100 - min(100, np.std(rolling_expectancy) / max(1, abs(np.mean(rolling_expectancy))) * 50)
        else:
            sharpe_stability = 0
            expectancy_stability = 0
        
        return {
            "rolling_sharpe": rolling_sharpe[-50:],  # Last 50 for chart
            "rolling_expectancy": rolling_expectancy[-50:],
            "rolling_win_rate": rolling_win_rate[-50:],
            "rolling_volatility": rolling_volatility[-50:],
            "dates": dates[-50:],
            "sharpe_stability": round(sharpe_stability, 2),
            "expectancy_stability": round(expectancy_stability, 2)
        }
    
    def _calculate_volatility_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate various volatility metrics"""
        returns = [t.get('profit_loss', 0) for t in trades]
        
        if len(returns) < 2:
            return {
                "daily_volatility": 0,
                "weekly_volatility": 0,
                "monthly_volatility": 0,
                "volatility_trend": "insufficient_data"
            }
        
        # Group by day for daily volatility
        daily_returns = defaultdict(list)
        for trade in trades:
            if trade.get('exit_time'):
                date = trade['exit_time'].split('T')[0]
                daily_returns[date].append(trade.get('profit_loss', 0))
        
        daily_vols = []
        for date, day_returns in daily_returns.items():
            if len(day_returns) > 1:
                daily_vols.append(np.std(day_returns))
        
        # Weekly grouping
        weekly_returns = defaultdict(list)
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    week = dt.strftime('%Y-%W')
                    weekly_returns[week].append(trade.get('profit_loss', 0))
                except:
                    continue
        
        weekly_vols = []
        for week, week_returns in weekly_returns.items():
            if len(week_returns) > 1:
                weekly_vols.append(np.std(week_returns))
        
        # Calculate volatility of volatility (volatility clustering)
        if len(weekly_vols) > 1:
            vol_of_vol = np.std(weekly_vols)
            vol_trend = "increasing" if weekly_vols[-1] > weekly_vols[0] else "decreasing" if weekly_vols[-1] < weekly_vols[0] else "stable"
        else:
            vol_of_vol = 0
            vol_trend = "insufficient_data"
        
        return {
            "daily_volatility": round(np.mean(daily_vols), 2) if daily_vols else 0,
            "weekly_volatility": round(np.mean(weekly_vols), 2) if weekly_vols else 0,
            "monthly_volatility": round(np.std(returns) * np.sqrt(20), 2),  # Approximate monthly
            "volatility_of_volatility": round(vol_of_vol, 2),
            "volatility_trend": vol_trend,
            "volatility_clustering": "high" if vol_of_vol > np.mean(weekly_vols) * 0.5 else "low" if weekly_vols else "unknown"
        }
    
    def _calculate_consistency_index(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate various consistency indices"""
        if len(trades) < 10:
            return {"overall": 0, "by_week": [], "by_month": []}
        
        # Overall consistency
        returns = [t.get('profit_loss', 0) for t in trades]
        positive_ratio = len([r for r in returns if r > 0]) / len(returns)
        
        if np.std(returns) > 0:
            consistency = (positive_ratio / (np.std(returns) / abs(np.mean(returns)) if np.mean(returns) != 0 else 1)) * 100
        else:
            consistency = positive_ratio * 100
        
        # Weekly consistency
        weekly_consistency = []
        weekly_groups = defaultdict(list)
        
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    week = dt.strftime('%Y-%W')
                    weekly_groups[week].append(trade.get('profit_loss', 0))
                except:
                    continue
        
        for week, week_returns in weekly_groups.items():
            if len(week_returns) >= 3:
                week_positive = len([r for r in week_returns if r > 0]) / len(week_returns)
                week_std = np.std(week_returns) if len(week_returns) > 1 else 1
                week_consistency = (week_positive / week_std) * 100
                weekly_consistency.append({
                    "week": week,
                    "score": round(min(100, week_consistency), 2),
                    "trades": len(week_returns)
                })
        
        return {
            "overall": round(min(100, consistency), 2),
            "by_week": weekly_consistency[-12:],  # Last 12 weeks
            "trend": "improving" if len(weekly_consistency) > 2 and weekly_consistency[-1]["score"] > weekly_consistency[0]["score"] else "declining" if len(weekly_consistency) > 2 else "stable"
        }
    
    def _calculate_equity_smoothness(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate equity curve smoothness metrics"""
        # Build equity curve
        equity = 10000
        equity_curve = [equity]
        
        for trade in trades:
            equity += trade.get('profit_loss', 0)
            equity_curve.append(equity)
        
        # Calculate smoothness metrics
        if len(equity_curve) < 3:
            return {"score": 0, "sharpe_ratio": 0, "ulcer_index": 0}
        
        # Calculate returns
        returns = np.diff(equity_curve) / equity_curve[:-1] * 100
        
        # Sharpe ratio of equity curve
        sharpe = self.formulas.calculate_sharpe_ratio(returns.tolist())
        
        # Ulcer Index (measures depth and duration of drawdowns)
        peak = equity_curve[0]
        drawdown_squares = []
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            drawdown_squares.append(drawdown ** 2)
        
        ulcer_index = np.sqrt(np.mean(drawdown_squares))
        
        # Smoothness score (lower ulcer index = smoother)
        if ulcer_index > 0:
            smoothness = max(0, 100 - min(100, ulcer_index * 5))
        else:
            smoothness = 100
        
        return {
            "score": round(smoothness, 2),
            "sharpe_ratio": round(sharpe, 2),
            "ulcer_index": round(ulcer_index, 2),
            "calmar_ratio": self.formulas.calculate_calmar_ratio(returns.tolist(), self._calculate_max_drawdown(equity_curve)),
            "equity_curve": [round(e, 2) for e in equity_curve[-100:]]  # Last 100 points for chart
        }
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown percentage"""
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _analyze_stability_trend(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze how stability is changing over time"""
        if len(trades) < 20:
            return {"trend": "insufficient_data", "acceleration": 0}
        
        # Split into periods
        third = len(trades) // 3
        period1 = trades[:third]
        period2 = trades[third:2*third]
        period3 = trades[2*third:]
        
        # Calculate stability for each period
        def period_stability(period_trades):
            returns = [t.get('profit_loss', 0) for t in period_trades]
            if len(returns) < 3:
                return 0
            positive_ratio = len([r for r in returns if r > 0]) / len(returns)
            std_returns = np.std(returns) if len(returns) > 1 else 1
            return (positive_ratio / std_returns) * 100 if std_returns > 0 else positive_ratio * 100
        
        stab1 = period_stability(period1)
        stab2 = period_stability(period2) if period2 else stab1
        stab3 = period_stability(period3) if period3 else stab2
        
        # Determine trend
        if stab3 > stab2 * 1.1:
            trend = "improving"
            acceleration = (stab3 - stab2) / abs(stab2) * 100 if stab2 != 0 else 0
        elif stab3 < stab2 * 0.9:
            trend = "declining"
            acceleration = (stab2 - stab3) / abs(stab2) * 100 if stab2 != 0 else 0
        else:
            trend = "stable"
            acceleration = 0
        
        return {
            "trend": trend,
            "acceleration": round(acceleration, 2),
            "period1_stability": round(stab1, 2),
            "period2_stability": round(stab2, 2),
            "period3_stability": round(stab3, 2)
        }
    
    def _calculate_stability_score(self, volatility: Dict, consistency: Dict, smoothness: Dict) -> float:
        """Calculate overall stability score (0-100)"""
        score = 0
        weights = {
            "volatility": 0.3,
            "consistency": 0.4,
            "smoothness": 0.3
        }
        
        # Volatility component (lower volatility = higher score)
        if volatility.get("weekly_volatility", 0) > 0:
            vol_score = max(0, 100 - min(100, volatility["weekly_volatility"] * 10))
            score += vol_score * weights["volatility"]
        
        # Consistency component
        if consistency.get("overall", 0) > 0:
            score += consistency["overall"] * weights["consistency"]
        
        # Smoothness component
        if smoothness.get("score", 0) > 0:
            score += smoothness["score"] * weights["smoothness"]
        
        return round(score, 2)
    
    def _get_stability_grade(self, score: float) -> Dict[str, Any]:
        """Get letter grade for stability score"""
        if score >= 90:
            return {"grade": "A+", "description": "Exceptional stability", "color": "green"}
        elif score >= 80:
            return {"grade": "A", "description": "Very stable", "color": "green"}
        elif score >= 70:
            return {"grade": "B+", "description": "Stable", "color": "blue"}
        elif score >= 60:
            return {"grade": "B", "description": "Moderately stable", "color": "blue"}
        elif score >= 50:
            return {"grade": "C+", "description": "Average stability", "color": "yellow"}
        elif score >= 40:
            return {"grade": "C", "description": "Below average stability", "color": "orange"}
        elif score >= 30:
            return {"grade": "D", "description": "Unstable", "color": "red"}
        else:
            return {"grade": "F", "description": "Highly unstable", "color": "red"}
    
    def _compare_to_benchmark(self, trades: List[Dict]) -> Dict[str, Any]:
        """Compare stability to benchmark (buy & hold)"""
        # Simple benchmark: S&P 500 proxy (random walk with drift)
        import random
        
        returns = [t.get('profit_loss', 0) for t in trades]
        if len(returns) < 10:
            return {"better_than_benchmark": False, "ratio": 0}
        
        # Generate benchmark returns (simplified)
        benchmark_returns = [random.gauss(0.05, 1.0) for _ in range(len(returns))]
        
        # Compare Sharpe ratios
        sharpe_actual = self.formulas.calculate_sharpe_ratio(returns)
        sharpe_benchmark = self.formulas.calculate_sharpe_ratio(benchmark_returns)
        
        if sharpe_benchmark > 0:
            ratio = sharpe_actual / sharpe_benchmark
        else:
            ratio = sharpe_actual if sharpe_actual > 0 else 0
        
        return {
            "better_than_benchmark": sharpe_actual > sharpe_benchmark,
            "ratio": round(ratio, 2),
            "sharpe_actual": round(sharpe_actual, 2),
            "sharpe_benchmark": round(sharpe_benchmark, 2)
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "rolling_metrics": {
                "rolling_sharpe": [], "rolling_expectancy": [], "rolling_win_rate": [],
                "rolling_volatility": [], "dates": [], "sharpe_stability": 0, "expectancy_stability": 0
            },
            "volatility_metrics": {
                "daily_volatility": 0, "weekly_volatility": 0, "monthly_volatility": 0,
                "volatility_of_volatility": 0, "volatility_trend": "no_data", "volatility_clustering": "unknown"
            },
            "consistency_index": {"overall": 0, "by_week": [], "trend": "no_data"},
            "equity_smoothness": {"score": 0, "sharpe_ratio": 0, "ulcer_index": 0, "calmar_ratio": 0, "equity_curve": []},
            "stability_trend": {"trend": "no_data", "acceleration": 0, "period1_stability": 0, "period2_stability": 0, "period3_stability": 0},
            "stability_score": 0,
            "stability_grade": {"grade": "N/A", "description": "Insufficient data", "color": "gray"},
            "comparison_to_benchmark": {"better_than_benchmark": False, "ratio": 0, "sharpe_actual": 0, "sharpe_benchmark": 0}
        }
