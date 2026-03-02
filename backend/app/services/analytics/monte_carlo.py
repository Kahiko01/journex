"""
Monte Carlo Simulation Service
Simulates thousands of trade sequences to predict risk and performance
"""

import numpy as np
import random
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import math

class MonteCarloService:
    
    def __init__(self):
        self.simulations = 1000  # Default number of simulations
        
    def simulate(self, trades: List[Dict], simulations: int = 1000, num_trades: int = None) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation on trade sequences
        """
        if len(trades) < 10:
            return self._empty_response()
        
        # Extract R multiples for simulation
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        if not r_values:
            r_values = [t.get('profit_loss', 0) / 100 for t in trades]  # Fallback to normalized P/L
        
        # Set number of trades to simulate (default: same as actual)
        if not num_trades:
            num_trades = len(trades)
        
        # Run simulations
        simulation_results = []
        equity_curves = []
        max_drawdowns = []
        max_drawdown_pcts = []
        final_equities = []
        
        initial_capital = 10000  # Starting capital
        
        for sim in range(simulations):
            # Randomly sample trades with replacement
            sampled_r = random.choices(r_values, k=num_trades)
            
            # Calculate equity curve
            equity = initial_capital
            curve = [equity]
            peak = equity
            max_dd = 0
            max_dd_pct = 0
            
            for r in sampled_r:
                # Convert R to P/L (assuming 1R = 1% risk)
                pl = equity * (r / 100)  # r is in R units, convert to percentage
                equity += pl
                curve.append(equity)
                
                # Track peak and drawdown
                if equity > peak:
                    peak = equity
                
                dd = peak - equity
                dd_pct = (dd / peak) * 100 if peak > 0 else 0
                
                max_dd = max(max_dd, dd)
                max_dd_pct = max(max_dd_pct, dd_pct)
            
            final_equities.append(equity)
            max_drawdowns.append(max_dd)
            max_drawdown_pcts.append(max_dd_pct)
            equity_curves.append(curve)
            
            simulation_results.append({
                "final_equity": equity,
                "total_return": ((equity - initial_capital) / initial_capital) * 100,
                "max_drawdown": max_dd,
                "max_drawdown_pct": max_dd_pct
            })
        
        # Calculate statistics
        final_equities = np.array(final_equities)
        max_drawdowns = np.array(max_drawdowns)
        max_drawdown_pcts = np.array(max_drawdown_pcts)
        
        # Confidence intervals
        def confidence_interval(data, confidence=0.95):
            mean = np.mean(data)
            sem = np.std(data) / np.sqrt(len(data))
            margin = sem * 1.96  # 95% confidence
            return mean - margin, mean + margin
        
        # Probability of drawdown > X%
        def probability_drawdown_exceeds(threshold_pct):
            count = len([dd for dd in max_drawdown_pcts if dd > threshold_pct])
            return count / len(max_drawdown_pcts) * 100
        
        # Calculate equity cloud for visualization (percentiles at each step)
        equity_cloud = self._calculate_equity_cloud(equity_curves)
        
        return {
            "simulation_stats": {
                "simulations_run": simulations,
                "trades_per_simulation": num_trades,
                "mean_final_equity": round(np.mean(final_equities), 2),
                "median_final_equity": round(np.median(final_equities), 2),
                "std_final_equity": round(np.std(final_equities), 2),
                "min_final_equity": round(np.min(final_equities), 2),
                "max_final_equity": round(np.max(final_equities), 2),
                "mean_return": round(np.mean([r["total_return"] for r in simulation_results]), 2),
                "median_return": round(np.median([r["total_return"] for r in simulation_results]), 2),
                "percentile_5_return": round(np.percentile([r["total_return"] for r in simulation_results], 5), 2),
                "percentile_95_return": round(np.percentile([r["total_return"] for r in simulation_results], 95), 2)
            },
            "drawdown_analysis": {
                "mean_max_drawdown": round(np.mean(max_drawdowns), 2),
                "mean_max_drawdown_pct": round(np.mean(max_drawdown_pcts), 2),
                "max_drawdown_pct_95_ci": [
                    round(confidence_interval(max_drawdown_pcts)[0], 2),
                    round(confidence_interval(max_drawdown_pcts)[1], 2)
                ],
                "probability_drawdown_exceeds_10": round(probability_drawdown_exceeds(10), 2),
                "probability_drawdown_exceeds_20": round(probability_drawdown_exceeds(20), 2),
                "probability_drawdown_exceeds_30": round(probability_drawdown_exceeds(30), 2),
                "probability_drawdown_exceeds_50": round(probability_drawdown_exceeds(50), 2)
            },
            "risk_of_ruin": {
                "probability_loss_gt_10": self._calculate_ruin_probability(final_equities, initial_capital, 0.1),
                "probability_loss_gt_25": self._calculate_ruin_probability(final_equities, initial_capital, 0.25),
                "probability_loss_gt_50": self._calculate_ruin_probability(final_equities, initial_capital, 0.5),
                "probability_loss_gt_75": self._calculate_ruin_probability(final_equities, initial_capital, 0.75)
            },
            "equity_cloud": equity_cloud,
            "distribution": {
                "final_equity_histogram": self._create_histogram(final_equities, 20),
                "max_drawdown_histogram": self._create_histogram(max_drawdown_pcts, 20)
            },
            "best_case": max(simulation_results, key=lambda x: x["final_equity"]),
            "worst_case": min(simulation_results, key=lambda x: x["final_equity"]),
            "typical_case": sorted(simulation_results, key=lambda x: x["final_equity"])[len(simulation_results)//2]
        }
    
    def _calculate_equity_cloud(self, equity_curves: List[List[float]]) -> Dict[str, Any]:
        """Calculate percentiles for equity cloud visualization"""
        # Find max length
        max_length = max(len(curve) for curve in equity_curves)
        
        # Pad curves to same length
        padded_curves = []
        for curve in equity_curves:
            if len(curve) < max_length:
                curve = curve + [curve[-1]] * (max_length - len(curve))
            padded_curves.append(curve)
        
        # Calculate percentiles at each step
        percentiles = {
            "p5": [],
            "p25": [],
            "p50": [],
            "p75": [],
            "p95": []
        }
        
        for step in range(max_length):
            step_values = [curve[step] for curve in padded_curves]
            percentiles["p5"].append(round(np.percentile(step_values, 5), 2))
            percentiles["p25"].append(round(np.percentile(step_values, 25), 2))
            percentiles["p50"].append(round(np.percentile(step_values, 50), 2))
            percentiles["p75"].append(round(np.percentile(step_values, 75), 2))
            percentiles["p95"].append(round(np.percentile(step_values, 95), 2))
        
        return percentiles
    
    def _create_histogram(self, data: np.ndarray, bins: int) -> List[Dict]:
        """Create histogram data for visualization"""
        hist, bin_edges = np.histogram(data, bins=bins)
        
        histogram_data = []
        for i in range(len(hist)):
            histogram_data.append({
                "bin_start": round(bin_edges[i], 2),
                "bin_end": round(bin_edges[i + 1], 2),
                "count": int(hist[i]),
                "percentage": round(hist[i] / len(data) * 100, 2)
            })
        
        return histogram_data
    
    def _calculate_ruin_probability(self, final_equities: np.ndarray, initial_capital: float, loss_threshold: float) -> float:
        """Calculate probability of losing more than threshold %"""
        threshold_value = initial_capital * (1 - loss_threshold)
        count = len([eq for eq in final_equities if eq < threshold_value])
        return round(count / len(final_equities) * 100, 2)
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "simulation_stats": {
                "simulations_run": 0, "trades_per_simulation": 0, "mean_final_equity": 0,
                "median_final_equity": 0, "std_final_equity": 0, "min_final_equity": 0,
                "max_final_equity": 0, "mean_return": 0, "median_return": 0,
                "percentile_5_return": 0, "percentile_95_return": 0
            },
            "drawdown_analysis": {
                "mean_max_drawdown": 0, "mean_max_drawdown_pct": 0,
                "max_drawdown_pct_95_ci": [0, 0],
                "probability_drawdown_exceeds_10": 0, "probability_drawdown_exceeds_20": 0,
                "probability_drawdown_exceeds_30": 0, "probability_drawdown_exceeds_50": 0
            },
            "risk_of_ruin": {
                "probability_loss_gt_10": 0, "probability_loss_gt_25": 0,
                "probability_loss_gt_50": 0, "probability_loss_gt_75": 0
            },
            "equity_cloud": {"p5": [], "p25": [], "p50": [], "p75": [], "p95": []},
            "distribution": {
                "final_equity_histogram": [],
                "max_drawdown_histogram": []
            },
            "best_case": {"final_equity": 0, "total_return": 0, "max_drawdown": 0, "max_drawdown_pct": 0},
            "worst_case": {"final_equity": 0, "total_return": 0, "max_drawdown": 0, "max_drawdown_pct": 0},
            "typical_case": {"final_equity": 0, "total_return": 0, "max_drawdown": 0, "max_drawdown_pct": 0}
        }
