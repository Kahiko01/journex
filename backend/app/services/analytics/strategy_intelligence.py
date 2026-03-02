"""
Strategy Intelligence Service
Analyzes performance by strategy
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from .formulas.mathematical_formulas import TradingFormulas

class StrategyIntelligenceService:
    
    def __init__(self):
        self.formulas = TradingFormulas()
    
    def analyze_strategies(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive strategy analysis
        """
        if not trades:
            return self._empty_response()
        
        # Group trades by strategy
        strategies = defaultdict(list)
        for trade in trades:
            strategy = trade.get('strategy', 'unspecified')
            if not strategy:
                strategy = 'unspecified'
            strategies[strategy].append(trade)
        
        # Analyze each strategy
        strategy_analyses = {}
        for strategy_name, strategy_trades in strategies.items():
            strategy_analyses[strategy_name] = self._analyze_single_strategy(strategy_name, strategy_trades)
        
        # Create comparison data
        comparison = self._create_strategy_comparison(strategy_analyses)
        
        # Find best and worst strategies
        best_strategy = self._find_best_strategy(strategy_analyses)
        worst_strategy = self._find_worst_strategy(strategy_analyses)
        
        return {
            "strategies": strategy_analyses,
            "comparison": comparison,
            "best_strategy": best_strategy,
            "worst_strategy": worst_strategy,
            "total_strategies": len(strategies),
            "strategy_diversity_score": self._calculate_diversity_score(strategies)
        }
    
    def _analyze_single_strategy(self, name: str, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze a single strategy"""
        if not trades:
            return self._empty_strategy()
        
        # Calculate core metrics
        profit_losses = [t.get('profit_loss', 0) for t in trades]
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        # Calculate drawdown for this strategy
        equity = 10000
        equity_curve = [equity]
        peak = equity
        
        for trade in trades:
            equity += trade.get('profit_loss', 0)
            equity_curve.append(equity)
            if equity > peak:
                peak = equity
        
        max_drawdown = 0
        for value in equity_curve:
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate trade duration patterns
        durations = []
        for trade in trades:
            if trade.get('entry_time') and trade.get('exit_time'):
                try:
                    entry = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
                    exit = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    duration = (exit - entry).total_seconds() / 3600  # hours
                    durations.append(duration)
                except:
                    continue
        
        # Session analysis
        sessions = defaultdict(list)
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    hour = dt.hour
                    if 0 <= hour < 8:
                        session = "Asia"
                    elif 8 <= hour < 16:
                        session = "London"
                    else:
                        session = "New York"
                    sessions[session].append(trade.get('profit_loss', 0))
                except:
                    continue
        
        session_performance = []
        for session, pls in sessions.items():
            session_performance.append({
                "session": session,
                "avg_pl": round(np.mean(pls), 2),
                "count": len(pls),
                "win_rate": round(len([p for p in pls if p > 0]) / len(pls) * 100, 2) if pls else 0
            })
        
        return {
            "name": name,
            "metrics": {
                "total_trades": len(trades),
                "win_rate": round(win_rate, 2),
                "avg_r": round(np.mean(r_values), 2) if r_values else 0,
                "median_r": round(np.median(r_values), 2) if r_values else 0,
                "profit_factor": self.formulas.calculate_profit_factor(trades),
                "payoff_ratio": self.formulas.calculate_payoff_ratio(trades),
                "total_pl": round(sum(profit_losses), 2),
                "avg_pl": round(np.mean(profit_losses), 2),
                "expectancy": self.formulas.calculate_expectancy(trades),
                "max_drawdown": round(max_drawdown, 2),
                "risk_efficiency": self._calculate_risk_efficiency(trades),
                "sharpe_ratio": self.formulas.calculate_sharpe_ratio(profit_losses)
            },
            "distribution": {
                "r_values": [round(r, 2) for r in r_values[-50:]],  # Last 50 for chart
                "pls": [round(pl, 2) for pl in profit_losses[-50:]],
                "avg_duration_hours": round(np.mean(durations), 1) if durations else 0,
                "median_duration_hours": round(np.median(durations), 1) if durations else 0
            },
            "sessions": session_performance,
            "consistency_score": self._calculate_strategy_consistency(trades)
        }
    
    def _create_strategy_comparison(self, strategies: Dict[str, Dict]) -> Dict[str, Any]:
        """Create comparison data for all strategies"""
        comparison_data = []
        
        for name, analysis in strategies.items():
            comparison_data.append({
                "name": name,
                "win_rate": analysis["metrics"]["win_rate"],
                "avg_r": analysis["metrics"]["avg_r"],
                "profit_factor": analysis["metrics"]["profit_factor"],
                "total_pl": analysis["metrics"]["total_pl"],
                "total_trades": analysis["metrics"]["total_trades"],
                "max_drawdown": analysis["metrics"]["max_drawdown"],
                "consistency": analysis["consistency_score"],
                "expectancy": analysis["metrics"]["expectancy"]
            })
        
        # Sort by different metrics for comparison
        comparison_data.sort(key=lambda x: x["total_pl"], reverse=True)
        
        return {
            "by_profit": comparison_data[:10],  # Top 10 by profit
            "by_win_rate": sorted(comparison_data, key=lambda x: x["win_rate"], reverse=True)[:10],
            "by_consistency": sorted(comparison_data, key=lambda x: x["consistency"], reverse=True)[:10],
            "by_sharpe": sorted(comparison_data, key=lambda x: x.get("expectancy", 0), reverse=True)[:10]
        }
    
    def _calculate_risk_efficiency(self, trades: List[Dict]) -> float:
        """Calculate risk efficiency for a strategy"""
        if len(trades) < 5:
            return 0
        
        # Calculate return per unit of risk
        total_return = sum(t.get('profit_loss', 0) for t in trades)
        
        # Calculate average risk (using stop loss as proxy)
        risks = []
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price'):
                risk_pct = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                risks.append(risk_pct)
        
        if not risks:
            return 0
        
        avg_risk = np.mean(risks)
        if avg_risk == 0:
            return 0
        
        return round(total_return / avg_risk, 2)
    
    def _calculate_strategy_consistency(self, trades: List[Dict]) -> float:
        """Calculate consistency score for a strategy"""
        if len(trades) < 10:
            return 0
        
        # Split into halves and compare performance
        half = len(trades) // 2
        first_half = trades[:half]
        second_half = trades[half:]
        
        first_win_rate = len([t for t in first_half if t.get('profit_loss', 0) > 0]) / len(first_half) * 100
        second_win_rate = len([t for t in second_half if t.get('profit_loss', 0) > 0]) / len(second_half) * 100
        
        # Calculate consistency based on win rate stability
        consistency = 100 - abs(second_win_rate - first_win_rate)
        
        return round(max(0, min(100, consistency)), 2)
    
    def _find_best_strategy(self, strategies: Dict[str, Dict]) -> Dict[str, Any]:
        """Find the best performing strategy"""
        if not strategies:
            return {"name": "none", "score": 0}
        
        best_name = None
        best_score = -float('inf')
        
        for name, analysis in strategies.items():
            # Composite score based on multiple factors
            score = (
                analysis["metrics"]["win_rate"] * 0.3 +
                analysis["metrics"]["profit_factor"] * 20 * 0.3 +
                analysis["consistency_score"] * 0.2 +
                analysis["metrics"]["expectancy"] * 0.2
            )
            
            if score > best_score:
                best_score = score
                best_name = name
        
        return {
            "name": best_name,
            "score": round(best_score, 2),
            "metrics": strategies[best_name]["metrics"] if best_name else {}
        }
    
    def _find_worst_strategy(self, strategies: Dict[str, Dict]) -> Dict[str, Any]:
        """Find the worst performing strategy"""
        if not strategies:
            return {"name": "none", "score": 0}
        
        worst_name = None
        worst_score = float('inf')
        
        for name, analysis in strategies.items():
            if analysis["metrics"]["total_trades"] < 5:
                continue  # Skip strategies with too few trades
                
            # Composite score (lower is worse)
            score = (
                analysis["metrics"]["win_rate"] * 0.3 +
                analysis["metrics"]["profit_factor"] * 20 * 0.3 +
                analysis["consistency_score"] * 0.2 +
                analysis["metrics"]["expectancy"] * 0.2
            )
            
            if score < worst_score:
                worst_score = score
                worst_name = name
        
        if not worst_name:
            return {"name": "none", "score": 0}
        
        return {
            "name": worst_name,
            "score": round(worst_score, 2),
            "metrics": strategies[worst_name]["metrics"]
        }
    
    def _calculate_diversity_score(self, strategies: Dict) -> float:
        """Calculate strategy diversity score"""
        if not strategies:
            return 0
        
        total_trades = sum(len(t) for t in strategies.values())
        if total_trades == 0:
            return 0
        
        # Calculate entropy of strategy distribution
        proportions = [len(t) / total_trades for t in strategies.values()]
        entropy = -sum(p * np.log(p) for p in proportions)
        
        # Normalize to 0-100 scale (max entropy = log(n))
        max_entropy = np.log(len(strategies))
        if max_entropy == 0:
            return 0
        
        diversity = entropy / max_entropy * 100
        return round(diversity, 2)
    
    def _empty_strategy(self) -> Dict[str, Any]:
        """Return empty strategy analysis"""
        return {
            "metrics": {
                "total_trades": 0, "win_rate": 0, "avg_r": 0, "median_r": 0,
                "profit_factor": 0, "payoff_ratio": 0, "total_pl": 0, "avg_pl": 0,
                "expectancy": 0, "max_drawdown": 0, "risk_efficiency": 0, "sharpe_ratio": 0
            },
            "distribution": {"r_values": [], "pls": [], "avg_duration_hours": 0, "median_duration_hours": 0},
            "sessions": [],
            "consistency_score": 0
        }
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "strategies": {},
            "comparison": {"by_profit": [], "by_win_rate": [], "by_consistency": [], "by_sharpe": []},
            "best_strategy": {"name": "none", "score": 0},
            "worst_strategy": {"name": "none", "score": 0},
            "total_strategies": 0,
            "strategy_diversity_score": 0
        }
