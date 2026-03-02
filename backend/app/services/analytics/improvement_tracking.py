"""
Improvement & Decay Tracking Service
Tracks trader improvement, strategy decay, and performance trends
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from .formulas.mathematical_formulas import TradingFormulas

class ImprovementTrackingService:
    
    def __init__(self):
        self.formulas = TradingFormulas()
    
    def analyze_improvement(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive improvement and decay analysis
        """
        if len(trades) < 20:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Split into periods for comparison
        periods = self._split_into_periods(trades)
        
        # Calculate improvement metrics
        improvement_metrics = self._calculate_improvement_metrics(periods)
        
        # Detect decay
        decay_analysis = self._detect_decay(trades, periods)
        
        # Track trends
        trends = self._analyze_trends(trades)
        
        # Course impact (if applicable)
        course_impact = self._analyze_course_impact(trades)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(improvement_metrics, decay_analysis, trends)
        
        return {
            "improvement_metrics": improvement_metrics,
            "decay_analysis": decay_analysis,
            "trends": trends,
            "course_impact": course_impact,
            "recommendations": recommendations,
            "improvement_score": self._calculate_improvement_score(improvement_metrics, decay_analysis),
            "trajectory": self._determine_trajectory(improvement_metrics, decay_analysis)
        }
    
    def _split_into_periods(self, trades: List[Dict]) -> Dict[str, List[Dict]]:
        """Split trades into comparable periods"""
        total_trades = len(trades)
        
        # Split into thirds
        third = total_trades // 3
        
        periods = {
            "early": trades[:third],
            "middle": trades[third:2*third] if total_trades >= 2*third else [],
            "recent": trades[2*third:] if total_trades >= 2*third else trades[third:]
        }
        
        # Also split by time (last 30/60/90 days)
        now = datetime.now()
        
        periods["last_30_days"] = []
        periods["last_60_days"] = []
        periods["last_90_days"] = []
        
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    trade_date = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    days_ago = (now - trade_date).days
                    
                    if days_ago <= 30:
                        periods["last_30_days"].append(trade)
                    if days_ago <= 60:
                        periods["last_60_days"].append(trade)
                    if days_ago <= 90:
                        periods["last_90_days"].append(trade)
                except:
                    continue
        
        return periods
    
    def _calculate_improvement_metrics(self, periods: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate improvement between periods"""
        metrics = {}
        
        def get_period_metrics(period_trades):
            if not period_trades:
                return None
            
            pls = [t.get('profit_loss', 0) for t in period_trades]
            wins = len([p for p in pls if p > 0])
            
            return {
                "total_trades": len(period_trades),
                "total_pl": round(sum(pls), 2),
                "avg_pl": round(np.mean(pls), 2),
                "win_rate": round(wins / len(period_trades) * 100, 2) if period_trades else 0,
                "profit_factor": self.formulas.calculate_profit_factor(period_trades),
                "expectancy": self.formulas.calculate_expectancy(period_trades),
                "avg_r": round(np.mean([t.get('r_multiple', 0) for t in period_trades]), 2),
                "sharpe": self.formulas.calculate_sharpe_ratio(pls)
            }
        
        # Calculate for each period
        for period_name, period_trades in periods.items():
            metrics[period_name] = get_period_metrics(period_trades)
        
        # Calculate improvements
        improvements = {}
        if metrics.get("early") and metrics.get("recent"):
            early = metrics["early"]
            recent = metrics["recent"]
            
            improvements = {
                "pl_change": round(recent["avg_pl"] - early["avg_pl"], 2),
                "pl_change_pct": round((recent["avg_pl"] - early["avg_pl"]) / abs(early["avg_pl"]) * 100 if early["avg_pl"] != 0 else 0, 2),
                "win_rate_change": round(recent["win_rate"] - early["win_rate"], 2),
                "profit_factor_change": round(recent["profit_factor"] - early["profit_factor"], 2),
                "expectancy_change": round(recent["expectancy"] - early["expectancy"], 2),
                "sharpe_change": round(recent["sharpe"] - early["sharpe"], 2)
            }
        
        # Recent trend (last 30 vs previous 30)
        if metrics.get("last_30_days") and metrics.get("last_60_days"):
            recent_30 = metrics["last_30_days"]
            prev_30_count = len(metrics["last_60_days"]) - len(metrics["last_30_days"])
            
            if prev_30_count > 0:
                # Approximate previous 30 days
                prev_30_trades = periods["last_60_days"][:prev_30_count]
                if prev_30_trades:
                    prev_30_pls = [t.get('profit_loss', 0) for t in prev_30_trades]
                    prev_30_avg = np.mean(prev_30_pls) if prev_30_pls else 0
                    
                    improvements["momentum"] = round(recent_30["avg_pl"] - prev_30_avg, 2)
        
        return {
            "period_metrics": metrics,
            "improvements": improvements,
            "improving_areas": self._identify_improving_areas(improvements),
            "declining_areas": self._identify_declining_areas(improvements)
        }
    
    def _detect_decay(self, trades: List[Dict], periods: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Detect performance decay"""
        decay_signals = []
        
        # Signal 1: Decreasing win rate
        if periods.get("early") and periods.get("recent"):
            early_win_rate = len([t for t in periods["early"] if t.get('profit_loss', 0) > 0]) / len(periods["early"]) * 100
            recent_win_rate = len([t for t in periods["recent"] if t.get('profit_loss', 0) > 0]) / len(periods["recent"]) * 100
            
            if recent_win_rate < early_win_rate * 0.8:  # 20% decline
                decay_signals.append({
                    "type": "win_rate_decay",
                    "severity": "high" if recent_win_rate < early_win_rate * 0.6 else "medium",
                    "description": f"Win rate declined from {round(early_win_rate, 1)}% to {round(recent_win_rate, 1)}%"
                })
        
        # Signal 2: Increasing drawdowns
        if len(trades) > 30:
            # Calculate rolling max drawdown
            window = 20
            recent_drawdowns = []
            
            for i in range(len(trades) - window):
                window_trades = trades[i:i+window]
                equity = 10000
                peak = equity
                max_dd = 0
                
                for trade in window_trades:
                    equity += trade.get('profit_loss', 0)
                    if equity > peak:
                        peak = equity
                    dd = (peak - equity) / peak * 100
                    max_dd = max(max_dd, dd)
                
                recent_drawdowns.append(max_dd)
            
            if len(recent_drawdowns) > 10:
                early_dd = np.mean(recent_drawdowns[:5])
                late_dd = np.mean(recent_drawdowns[-5:])
                
                if late_dd > early_dd * 1.5:
                    decay_signals.append({
                        "type": "increasing_drawdowns",
                        "severity": "high" if late_dd > early_dd * 2 else "medium",
                        "description": f"Average drawdown increased from {round(early_dd, 1)}% to {round(late_dd, 1)}%"
                    })
        
        # Signal 3: Strategy degradation (if multiple strategies)
        strategies = defaultdict(list)
        for trade in trades[-50:]:  # Last 50 trades
            strategy = trade.get('strategy', 'unspecified')
            strategies[strategy].append(trade)
        
        degraded_strategies = []
        for strategy, strategy_trades in strategies.items():
            if len(strategy_trades) >= 10:
                half = len(strategy_trades) // 2
                first_half = strategy_trades[:half]
                second_half = strategy_trades[half:]
                
                first_pl = np.mean([t.get('profit_loss', 0) for t in first_half])
                second_pl = np.mean([t.get('profit_loss', 0) for t in second_half])
                
                if second_pl < first_pl * 0.5 and first_pl > 0:
                    degraded_strategies.append(strategy)
        
        # Signal 4: Risk creep
        if len(trades) > 30:
            recent_risks = []
            for trade in trades[-20:]:
                if trade.get('stop_loss') and trade.get('entry_price'):
                    risk = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                    recent_risks.append(risk)
            
            if recent_risks:
                avg_recent_risk = np.mean(recent_risks)
                older_risks = []
                for trade in trades[:20]:
                    if trade.get('stop_loss') and trade.get('entry_price'):
                        risk = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                        older_risks.append(risk)
                
                if older_risks and avg_recent_risk > np.mean(older_risks) * 1.3:
                    decay_signals.append({
                        "type": "risk_creep",
                        "severity": "medium",
                        "description": f"Average risk per trade increased from {round(np.mean(older_risks), 1)}% to {round(avg_recent_risk, 1)}%"
                    })
        
        return {
            "decay_signals": decay_signals,
            "decay_score": len(decay_signals) * 20,  # Simple score
            "degraded_strategies": degraded_strategies,
            "has_decay": len(decay_signals) > 0
        }
    
    def _analyze_trends(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends"""
        if len(trades) < 10:
            return {"trends": [], "momentum": "neutral"}
        
        # Calculate moving averages of performance
        window = min(10, len(trades) // 4)
        ma_short = []
        ma_long = []
        
        for i in range(len(trades) - window + 1):
            window_trades = trades[i:i+window]
            ma_short.append(np.mean([t.get('profit_loss', 0) for t in window_trades]))
        
        window_long = min(20, len(trades) // 2)
        for i in range(len(trades) - window_long + 1):
            window_trades = trades[i:i+window_long]
            ma_long.append(np.mean([t.get('profit_loss', 0) for t in window_trades]))
        
        # Determine trend
        if len(ma_short) > 5 and len(ma_long) > 5:
            short_slope = ma_short[-1] - ma_short[-5]
            long_slope = ma_long[-1] - ma_long[-5]
            
            if short_slope > 0 and long_slope > 0:
                momentum = "strong_uptrend"
            elif short_slope > 0 > long_slope:
                momentum = "reversal_up"
            elif short_slope < 0 < long_slope:
                momentum = "reversal_down"
            elif short_slope < 0 and long_slope < 0:
                momentum = "strong_downtrend"
            else:
                momentum = "neutral"
        else:
            momentum = "insufficient_data"
        
        # Identify specific trends
        trends = []
        
        # Win rate trend
        if len(trades) >= 20:
            recent_wins = len([t for t in trades[-10:] if t.get('profit_loss', 0) > 0])
            older_wins = len([t for t in trades[:10] if t.get('profit_loss', 0) > 0])
            
            if recent_wins > older_wins + 2:
                trends.append("win_rate_improving")
            elif recent_wins < older_wins - 2:
                trends.append("win_rate_declining")
        
        # Risk adjustment trend
        recent_r = np.mean([t.get('r_multiple', 0) for t in trades[-10:] if t.get('r_multiple')])
        older_r = np.mean([t.get('r_multiple', 0) for t in trades[:10] if t.get('r_multiple')])
        
        if recent_r > older_r * 1.2:
            trends.append("edge_expanding")
        elif recent_r < older_r * 0.8:
            trends.append("edge_contracting")
        
        return {
            "momentum": momentum,
            "trends": trends,
            "ma_short": ma_short[-20:] if ma_short else [],
            "ma_long": ma_long[-20:] if ma_long else []
        }
    
    def _analyze_course_impact(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze impact of trading courses (if any)"""
        # This would need course enrollment data
        # For now, return placeholder
        return {
            "has_course_data": False,
            "message": "No course enrollment data available"
        }
    
    def _generate_recommendations(self, improvement_metrics: Dict, decay_analysis: Dict, trends: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Based on decay signals
        for signal in decay_analysis.get("decay_signals", []):
            if signal["type"] == "win_rate_decay":
                recommendations.append("Your win rate is declining. Review your recent trades for pattern changes.")
            elif signal["type"] == "increasing_drawdowns":
                recommendations.append("Drawdowns are increasing. Consider reducing position sizes temporarily.")
            elif signal["type"] == "risk_creep":
                recommendations.append("You're taking more risk per trade. Stick to your original risk parameters.")
        
        # Based on trends
        if "edge_contracting" in trends.get("trends", []):
            recommendations.append("Your edge per trade is shrinking. Review your strategy for market adaptation.")
        
        # Based on improvements
        improvements = improvement_metrics.get("improvements", {})
        if improvements.get("pl_change_pct", 0) < -20:
            recommendations.append("Your average profit per trade has dropped significantly. Consider a performance review.")
        elif improvements.get("pl_change_pct", 0) > 20:
            recommendations.append("You're improving! Document what's working well.")
        
        # General recommendations
        if decay_analysis.get("has_decay"):
            recommendations.append("Consider taking a short break to reset and review your approach.")
        
        if not recommendations:
            recommendations.append("Your performance is stable. Focus on consistent execution.")
        
        return recommendations[:5]  # Max 5 recommendations
    
    def _calculate_improvement_score(self, improvement_metrics: Dict, decay_analysis: Dict) -> float:
        """Calculate overall improvement score (0-100)"""
        score = 50  # Start at neutral
        
        improvements = improvement_metrics.get("improvements", {})
        
        # Add for positive changes
        if improvements.get("pl_change_pct", 0) > 10:
            score += 10
        elif improvements.get("pl_change_pct", 0) > 5:
            score += 5
        elif improvements.get("pl_change_pct", 0) < -10:
            score -= 10
        elif improvements.get("pl_change_pct", 0) < -5:
            score -= 5
        
        if improvements.get("win_rate_change", 0) > 5:
            score += 10
        elif improvements.get("win_rate_change", 0) > 2:
            score += 5
        elif improvements.get("win_rate_change", 0) < -5:
            score -= 10
        elif improvements.get("win_rate_change", 0) < -2:
            score -= 5
        
        if improvements.get("sharpe_change", 0) > 0.5:
            score += 10
        elif improvements.get("sharpe_change", 0) > 0.2:
            score += 5
        elif improvements.get("sharpe_change", 0) < -0.5:
            score -= 10
        elif improvements.get("sharpe_change", 0) < -0.2:
            score -= 5
        
        # Subtract for decay
        score -= decay_analysis.get("decay_score", 0) * 0.5
        
        return round(max(0, min(100, score)), 2)
    
    def _determine_trajectory(self, improvement_metrics: Dict, decay_analysis: Dict) -> str:
        """Determine overall trajectory"""
        if decay_analysis.get("has_decay"):
            if improvement_metrics.get("improvements", {}).get("pl_change_pct", 0) > 0:
                return "mixed_signals"
            else:
                return "declining"
        else:
            if improvement_metrics.get("improvements", {}).get("pl_change_pct", 0) > 5:
                return "improving"
            elif improvement_metrics.get("improvements", {}).get("pl_change_pct", 0) < -5:
                return "declining"
            else:
                return "stable"
    
    def _identify_improving_areas(self, improvements: Dict) -> List[str]:
        """Identify areas showing improvement"""
        improving = []
        
        if improvements.get("win_rate_change", 0) > 3:
            improving.append("win_rate")
        if improvements.get("profit_factor_change", 0) > 0.3:
            improving.append("profit_factor")
        if improvements.get("expectancy_change", 0) > 5:
            improving.append("expectancy")
        if improvements.get("sharpe_change", 0) > 0.2:
            improving.append("risk_adjustment")
        
        return improving
    
    def _identify_declining_areas(self, improvements: Dict) -> List[str]:
        """Identify areas showing decline"""
        declining = []
        
        if improvements.get("win_rate_change", 0) < -3:
            declining.append("win_rate")
        if improvements.get("profit_factor_change", 0) < -0.3:
            declining.append("profit_factor")
        if improvements.get("expectancy_change", 0) < -5:
            declining.append("expectancy")
        if improvements.get("sharpe_change", 0) < -0.2:
            declining.append("risk_adjustment")
        
        return declining
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "improvement_metrics": {
                "period_metrics": {},
                "improvements": {},
                "improving_areas": [],
                "declining_areas": []
            },
            "decay_analysis": {
                "decay_signals": [],
                "decay_score": 0,
                "degraded_strategies": [],
                "has_decay": False
            },
            "trends": {
                "momentum": "insufficient_data",
                "trends": [],
                "ma_short": [],
                "ma_long": []
            },
            "course_impact": {
                "has_course_data": False,
                "message": "No course enrollment data available"
            },
            "recommendations": ["Add more trades to receive personalized recommendations"],
            "improvement_score": 0,
            "trajectory": "insufficient_data"
        }
