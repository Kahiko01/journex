"""
Risk Efficiency Engine
Measures how efficiently risk is utilized and managed
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from .formulas.mathematical_formulas import TradingFormulas

class RiskEfficiencyService:
    
    def __init__(self):
        self.formulas = TradingFormulas()
    
    def analyze_risk_efficiency(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive risk efficiency analysis
        """
        if not trades:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Core risk metrics
        risk_metrics = self._calculate_risk_metrics(trades)
        
        # Risk deviation analysis
        deviation = self._analyze_risk_deviation(trades)
        
        # Risk heatmap
        heatmap = self._generate_risk_heatmap(trades)
        
        # Risk vs performance
        risk_performance = self._risk_vs_performance(trades)
        
        # Risk consistency
        consistency = self._risk_consistency(trades)
        
        # Drawdown efficiency
        drawdown_efficiency = self._drawdown_efficiency(trades)
        
        return {
            "risk_metrics": risk_metrics,
            "risk_deviation": deviation,
            "risk_heatmap": heatmap,
            "risk_performance_scatter": risk_performance,
            "risk_consistency": consistency,
            "drawdown_efficiency": drawdown_efficiency,
            "risk_efficiency_score": self._calculate_risk_efficiency_score(trades)
        }
    
    def _calculate_risk_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate core risk metrics"""
        # Extract risk per trade (using stop loss or position size as proxy)
        risk_per_trade = []
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price'):
                risk_pct = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                risk_per_trade.append(risk_pct)
        
        # Calculate planned vs actual risk
        planned_risk = []
        actual_risk = []
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price'):
                planned = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                planned_risk.append(planned)
            
            if trade.get('exit_price') and trade.get('entry_price'):
                actual = abs(trade['entry_price'] - trade['exit_price']) / trade['entry_price'] * 100
                actual_risk.append(actual)
        
        # Risk utilization
        risk_utilization = []
        for p, a in zip(planned_risk, actual_risk):
            if p > 0:
                utilization = min(100, (a / p) * 100)
                risk_utilization.append(utilization)
        
        # Days exceeding allowed risk
        max_allowed_risk = 2.0  # 2% per trade (configurable)
        exceeding_days = []
        for trade in trades:
            if trade.get('exit_time'):
                date = trade['exit_time'].split('T')[0]
                risk = abs(trade.get('profit_loss', 0)) / 10000  # Simplified risk calculation
                if risk > max_allowed_risk:
                    exceeding_days.append({
                        "date": date,
                        "risk": round(risk, 2),
                        "symbol": trade.get('symbol', ''),
                        "excess": round(risk - max_allowed_risk, 2)
                    })
        
        return {
            "avg_planned_risk": round(np.mean(planned_risk), 2) if planned_risk else 0,
            "avg_actual_risk": round(np.mean(actual_risk), 2) if actual_risk else 0,
            "avg_risk_utilization": round(np.mean(risk_utilization), 2) if risk_utilization else 0,
            "risk_std_dev": round(np.std(planned_risk), 2) if len(planned_risk) > 1 else 0,
            "max_risk_taken": round(max(actual_risk), 2) if actual_risk else 0,
            "min_risk_taken": round(min(actual_risk), 2) if actual_risk else 0,
            "days_exceeding_risk": exceeding_days,
            "exceeding_days_count": len(exceeding_days),
            "risk_percentile": {
                "25th": round(np.percentile(actual_risk, 25), 2) if actual_risk else 0,
                "50th": round(np.percentile(actual_risk, 50), 2) if actual_risk else 0,
                "75th": round(np.percentile(actual_risk, 75), 2) if actual_risk else 0,
                "90th": round(np.percentile(actual_risk, 90), 2) if actual_risk else 0
            }
        }
    
    def _analyze_risk_deviation(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze deviation from planned risk"""
        deviations = []
        dates = []
        
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price') and trade.get('exit_price'):
                planned = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                actual = abs(trade['entry_price'] - trade['exit_price']) / trade['entry_price'] * 100
                
                deviation = actual - planned
                deviations.append(deviation)
                dates.append(trade.get('exit_time', ''))
        
        if not deviations:
            return {"deviation_data": [], "avg_deviation": 0, "std_deviation": 0}
        
        # Create deviation chart data
        deviation_data = []
        for i, (date, dev) in enumerate(zip(dates, deviations)):
            deviation_data.append({
                "date": date,
                "deviation": round(dev, 2),
                "positive": dev > 0
            })
        
        return {
            "deviation_data": deviation_data,
            "avg_deviation": round(np.mean(deviations), 2),
            "std_deviation": round(np.std(deviations), 2) if len(deviations) > 1 else 0,
            "max_positive_deviation": round(max(deviations), 2),
            "max_negative_deviation": round(min(deviations), 2),
            "positive_deviations": len([d for d in deviations if d > 0]),
            "negative_deviations": len([d for d in deviations if d < 0])
        }
    
    def _generate_risk_heatmap(self, trades: List[Dict]) -> Dict[str, Any]:
        """Generate risk heatmap data"""
        # Group by day and hour
        heatmap_data = defaultdict(lambda: defaultdict(list))
        
        for trade in trades:
            if trade.get('exit_time'):
                dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                date_key = dt.strftime('%Y-%m-%d')
                hour_key = dt.hour
                
                risk = abs(trade.get('profit_loss', 0)) / 100  # Normalize risk
                heatmap_data[date_key][hour_key].append(risk)
        
        # Convert to format suitable for heatmap
        days = sorted(heatmap_data.keys())
        hours = list(range(24))
        
        heatmap_matrix = []
        for day in days[-30:]:  # Last 30 days
            row = []
            for hour in hours:
                risks = heatmap_data[day][hour]
                if risks:
                    avg_risk = np.mean(risks)
                    # Color intensity based on risk level
                    intensity = min(1.0, avg_risk / 5)  # Cap at 5% risk
                    row.append({
                        "risk": round(avg_risk, 2),
                        "intensity": round(intensity, 2),
                        "trades": len(risks)
                    })
                else:
                    row.append({"risk": 0, "intensity": 0, "trades": 0})
            heatmap_matrix.append(row)
        
        return {
            "days": days[-30:],
            "hours": hours,
            "heatmap": heatmap_matrix,
            "max_risk": max([cell["risk"] for row in heatmap_matrix for cell in row]) if heatmap_matrix else 0
        }
    
    def _risk_vs_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Create risk vs performance scatter plot data"""
        scatter_data = []
        
        for trade in trades:
            if trade.get('exit_price') and trade.get('entry_price'):
                risk = abs(trade.get('profit_loss', 0)) / 100  # Normalize risk
                performance = trade.get('r_multiple', 0)
                
                scatter_data.append({
                    "risk": round(risk, 2),
                    "performance": round(performance, 2),
                    "symbol": trade.get('symbol', ''),
                    "profitable": performance > 0,
                    "size": abs(trade.get('lot_size', 1)) * 2  # Bubble size
                })
        
        # Calculate correlation
        if len(scatter_data) > 1:
            risks = [d["risk"] for d in scatter_data]
            performances = [d["performance"] for d in scatter_data]
            correlation = np.corrcoef(risks, performances)[0, 1]
        else:
            correlation = 0
        
        return {
            "scatter_data": scatter_data,
            "correlation": round(correlation, 3),
            "total_points": len(scatter_data)
        }
    
    def _risk_consistency(self, trades: List[Dict]) -> Dict[str, Any]:
        """Measure risk consistency over time"""
        if len(trades) < 10:
            return {"score": 0, "trend": "insufficient_data"}
        
        # Calculate rolling risk standard deviation
        window = 10
        rolling_risk_std = []
        dates = []
        
        for i in range(len(trades) - window + 1):
            window_trades = trades[i:i + window]
            risks = [abs(t.get('profit_loss', 0)) / 100 for t in window_trades]
            rolling_risk_std.append(np.std(risks))
            dates.append(trades[i + window - 1].get('exit_time', ''))
        
        # Calculate consistency score (lower std deviation is better)
        if rolling_risk_std:
            avg_std = np.mean(rolling_risk_std)
            consistency_score = max(0, 100 - min(100, avg_std * 20))
        else:
            consistency_score = 0
        
        # Determine trend
        if len(rolling_risk_std) > 5:
            first_half = rolling_risk_std[:len(rolling_risk_std)//2]
            second_half = rolling_risk_std[len(rolling_risk_std)//2:]
            
            if np.mean(second_half) < np.mean(first_half) * 0.8:
                trend = "improving"
            elif np.mean(second_half) > np.mean(first_half) * 1.2:
                trend = "deteriorating"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "score": round(consistency_score, 2),
            "trend": trend,
            "rolling_risk_std": [round(x, 2) for x in rolling_risk_std],
            "dates": dates
        }
    
    def _drawdown_efficiency(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate drawdown efficiency metrics"""
        # Calculate equity curve
        equity = 10000  # Starting equity
        equity_curve = [equity]
        dates = []
        
        for trade in trades:
            equity += trade.get('profit_loss', 0)
            equity_curve.append(equity)
            dates.append(trade.get('exit_time', ''))
        
        # Calculate drawdowns
        drawdowns = []
        peak = equity_curve[0]
        
        for value in equity_curve[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            drawdowns.append(drawdown)
        
        # Calculate efficiency
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        drawdown_efficiency = total_return / max_drawdown if max_drawdown > 0 else 0
        
        # Recovery time
        recovery_times = []
        in_drawdown = False
        drawdown_start = None
        
        for i, (date, value) in enumerate(zip(dates, equity_curve[1:])):
            if not in_drawdown and value < peak:
                in_drawdown = True
                drawdown_start = i
            elif in_drawdown and value >= peak:
                in_drawdown = False
                recovery_time = i - drawdown_start
                recovery_times.append(recovery_time)
        
        return {
            "efficiency_ratio": round(drawdown_efficiency, 2),
            "total_return": round(total_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "avg_recovery_time": round(np.mean(recovery_times), 1) if recovery_times else 0,
            "max_recovery_time": max(recovery_times) if recovery_times else 0,
            "drawdowns": [round(d, 2) for d in drawdowns],
            "dates": dates
        }
    
    def _calculate_risk_efficiency_score(self, trades: List[Dict]) -> float:
        """Calculate overall risk efficiency score (0-100)"""
        if len(trades) < 5:
            return 0
        
        score = 0
        
        # Factor 1: Risk utilization (30 points)
        risk_metrics = self._calculate_risk_metrics(trades)
        utilization = risk_metrics.get('avg_risk_utilization', 0)
        if 70 <= utilization <= 90:  # Optimal utilization
            score += 30
        elif 50 <= utilization <= 95:
            score += 20
        elif utilization > 0:
            score += 10
        
        # Factor 2: Risk consistency (30 points)
        risk_std = risk_metrics.get('risk_std_dev', 100)
        if risk_std < 0.5:
            score += 30
        elif risk_std < 1:
            score += 20
        elif risk_std < 2:
            score += 10
        
        # Factor 3: Days exceeding risk (20 points)
        exceeding_pct = risk_metrics.get('exceeding_days_count', 0) / max(1, len(trades)) * 100
        if exceeding_pct == 0:
            score += 20
        elif exceeding_pct < 5:
            score += 15
        elif exceeding_pct < 10:
            score += 10
        elif exceeding_pct < 20:
            score += 5
        
        # Factor 4: Drawdown efficiency (20 points)
        drawdown_eff = self._drawdown_efficiency(trades).get('efficiency_ratio', 0)
        if drawdown_eff > 5:
            score += 20
        elif drawdown_eff > 3:
            score += 15
        elif drawdown_eff > 1:
            score += 10
        elif drawdown_eff > 0:
            score += 5
        
        return round(score, 2)
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "risk_metrics": {
                "avg_planned_risk": 0, "avg_actual_risk": 0, "avg_risk_utilization": 0,
                "risk_std_dev": 0, "max_risk_taken": 0, "min_risk_taken": 0,
                "days_exceeding_risk": [], "exceeding_days_count": 0,
                "risk_percentile": {"25th": 0, "50th": 0, "75th": 0, "90th": 0}
            },
            "risk_deviation": {
                "deviation_data": [], "avg_deviation": 0, "std_deviation": 0,
                "max_positive_deviation": 0, "max_negative_deviation": 0,
                "positive_deviations": 0, "negative_deviations": 0
            },
            "risk_heatmap": {"days": [], "hours": [], "heatmap": [], "max_risk": 0},
            "risk_performance_scatter": {"scatter_data": [], "correlation": 0, "total_points": 0},
            "risk_consistency": {"score": 0, "trend": "no_data", "rolling_risk_std": [], "dates": []},
            "drawdown_efficiency": {
                "efficiency_ratio": 0, "total_return": 0, "max_drawdown": 0,
                "avg_recovery_time": 0, "max_recovery_time": 0, "drawdowns": [], "dates": []
            },
            "risk_efficiency_score": 0
        }
