"""
Edge Quality Analysis Service
Measures the quality and consistency of trading edge
"""

import numpy as np

def convert_numpy(obj):
    """Convert numpy types to native Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy(item) for item in obj)
    elif hasattr(obj, 'item'):
        return obj.item()
    else:
        return obj
import numpy as np

def convert_numpy(obj):
    """Convert numpy types to native Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy(item) for item in obj)
    elif hasattr(obj, 'item'):
        return obj.item()
    else:
        return obj
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from scipy import stats
from .formulas.mathematical_formulas import TradingFormulas

class EdgeQualityService:
    
    def __init__(self):
        self.formulas = TradingFormulas()
    
    def analyze_edge_quality(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive edge quality analysis
        """
        if not trades:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Core metrics
        core_metrics = self._calculate_core_metrics(trades)
        
        # Distribution analysis
        distribution = self._analyze_distribution(trades)
        
        # Rolling analysis
        rolling_analysis = self._rolling_performance(trades)
        
        # Statistical significance
        significance = self._statistical_significance(trades)
        
        # Edge consistency
        consistency = self._edge_consistency(trades)
        
        return {
            "core_metrics": core_metrics,
            "distribution": distribution,
            "rolling_analysis": rolling_analysis,
            "statistical_significance": significance,
            "edge_consistency": consistency,
            "sample_size_warning": len(trades) < 30,
            "reliability_score": self._calculate_reliability(trades)
        }
    
    def _calculate_core_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate core edge metrics"""
        profit_losses = [t.get('profit_loss', 0) for t in trades]
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        return {
            "expectancy": self.formulas.calculate_expectancy(trades),
            "expectancy_r": np.mean([t.get('r_multiple', 0) for t in trades]) if r_values else 0,
            "average_r": np.mean(r_values) if r_values else 0,
            "median_r": np.median(r_values) if r_values else 0,
            "std_dev_r": np.std(r_values) if len(r_values) > 1 else 0,
            "sharpe_ratio": self.formulas.calculate_sharpe_ratio(profit_losses),
            "profit_factor": self.formulas.calculate_profit_factor(trades),
            "payoff_ratio": self.formulas.calculate_payoff_ratio(trades),
            "win_rate": round(win_rate, 2),
            "avg_win": np.mean([t['profit_loss'] for t in winning_trades]) if winning_trades else 0,
            "avg_loss": abs(np.mean([t['profit_loss'] for t in losing_trades])) if losing_trades else 0,
            "largest_win": max(profit_losses) if profit_losses else 0,
            "largest_loss": min(profit_losses) if profit_losses else 0,
            "win_streak": self._calculate_max_streak(trades, 'win'),
            "loss_streak": self._calculate_max_streak(trades, 'loss')
        }
    
    def _analyze_distribution(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze the distribution of R multiples"""
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        
        if len(r_values) < 2:
            return {
                "histogram_data": [],
                "skewness": 0,
                "kurtosis": 0,
                "normality_test": None
            }
        
        # Create histogram data for frontend
        hist, bin_edges = np.histogram(r_values, bins='auto')
        
        histogram_data = []
        for i in range(len(hist)):
            histogram_data.append({
                "bin_start": round(bin_edges[i], 2),
                "bin_end": round(bin_edges[i + 1], 2),
                "count": int(hist[i]),
                "percentage": round(hist[i] / len(r_values) * 100, 2)
            })
        
        # Calculate skewness and kurtosis
        skewness = float(stats.skew(r_values))
        kurtosis = float(stats.kurtosis(r_values))
        
        # Shapiro-Wilk test for normality (if sample size allows)
        normality_test = None
        if len(r_values) >= 3 and len(r_values) <= 5000:
            statistic, p_value = stats.shapiro(r_values[:5000])  # Limit to 5000 for performance
            normality_test = {
                "statistic": round(statistic, 4),
                "p_value": round(p_value, 4),
                "is_normal": p_value > 0.05
            }
        
        return {
            "histogram_data": histogram_data,
            "skewness": round(skewness, 3),
            "kurtosis": round(kurtosis, 3),
            "normality_test": normality_test,
            "percentiles": {
                "10th": round(np.percentile(r_values, 10), 2),
                "25th": round(np.percentile(r_values, 25), 2),
                "50th": round(np.percentile(r_values, 50), 2),
                "75th": round(np.percentile(r_values, 75), 2),
                "90th": round(np.percentile(r_values, 90), 2)
            }
        }
    
    def _rolling_performance(self, trades: List[Dict], window: int = 20) -> Dict[str, Any]:
        """Calculate rolling performance metrics"""
        if len(trades) < window:
            return {
                "rolling_expectancy": [],
                "rolling_win_rate": [],
                "rolling_r_multiple": [],
                "dates": []
            }
        
        rolling_expectancy = []
        rolling_win_rate = []
        rolling_r = []
        dates = []
        
        for i in range(len(trades) - window + 1):
            window_trades = trades[i:i + window]
            
            # Calculate metrics for this window
            expectancy = self.formulas.calculate_expectancy(window_trades)
            win_rate = len([t for t in window_trades if t.get('profit_loss', 0) > 0]) / window * 100
            avg_r = np.mean([t.get('r_multiple', 0) for t in window_trades])
            
            rolling_expectancy.append(expectancy)
            rolling_win_rate.append(round(win_rate, 2))
            rolling_r.append(round(avg_r, 2))
            dates.append(trades[i + window - 1].get('exit_time', ''))
        
        # Calculate confidence intervals
        if len(rolling_expectancy) > 1:
            mean_exp = np.mean(rolling_expectancy)
            std_exp = np.std(rolling_expectancy)
            confidence_interval = {
                "lower": mean_exp - 1.96 * std_exp / np.sqrt(len(rolling_expectancy)),
                "upper": mean_exp + 1.96 * std_exp / np.sqrt(len(rolling_expectancy))
            }
        else:
            confidence_interval = {"lower": 0, "upper": 0}
        
        return {
            "rolling_expectancy": rolling_expectancy,
            "rolling_win_rate": rolling_win_rate,
            "rolling_r_multiple": rolling_r,
            "dates": dates,
            "confidence_interval": confidence_interval
        }
    
    def _statistical_significance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Test statistical significance of edge"""
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        
        if len(r_values) < 2:
            return {"significant": False, "t_statistic": 0, "p_value": 1}
        
        # One-sample t-test against null hypothesis (mean = 0)
        t_statistic, p_value = stats.ttest_1samp(r_values, 0)
        
        return {
            "significant": p_value < 0.05,
            "t_statistic": round(t_statistic, 3),
            "p_value": round(p_value, 4),
            "confidence_level": "95%" if p_value < 0.05 else "Not significant"
        }
    
    def _edge_consistency(self, trades: List[Dict]) -> Dict[str, Any]:
        """Measure consistency of edge over time"""
        if len(trades) < 10:
            return {"score": 0, "trend": "insufficient_data"}
        
        # Split trades into halves and compare
        half = len(trades) // 2
        first_half = trades[:half]
        second_half = trades[half:]
        
        first_expectancy = self.formulas.calculate_expectancy(first_half)
        second_expectancy = self.formulas.calculate_expectancy(second_half)
        
        # Calculate consistency score
        if first_expectancy == 0:
            consistency_score = 0
        else:
            consistency_score = min(100, (second_expectancy / first_expectancy) * 100)
        
        # Determine trend
        if second_expectancy > first_expectancy * 1.1:
            trend = "improving"
        elif second_expectancy < first_expectancy * 0.9:
            trend = "decaying"
        else:
            trend = "stable"
        
        return {
            "score": round(consistency_score, 2),
            "trend": trend,
            "first_half_expectancy": round(first_expectancy, 2),
            "second_half_expectancy": round(second_expectancy, 2),
            "change_percent": round((second_expectancy - first_expectancy) / abs(first_expectancy) * 100 if first_expectancy != 0 else 0, 2)
        }
    
    def _calculate_reliability(self, trades: List[Dict]) -> float:
        """Calculate reliability score based on sample size and consistency"""
        if len(trades) < 10:
            return 0
        
        sample_size_score = min(100, len(trades) / 3)  # 300 trades = 100%
        
        r_values = [t.get('r_multiple', 0) for t in trades]
        if len(r_values) > 1:
            cv = np.std(r_values) / abs(np.mean(r_values)) if np.mean(r_values) != 0 else float('inf')
            consistency_score = max(0, 100 - min(100, cv * 50))
        else:
            consistency_score = 0
        
        return round((sample_size_score + consistency_score) / 2, 2)
    
    def _calculate_max_streak(self, trades: List[Dict], streak_type: str) -> int:
        """Calculate maximum consecutive wins or losses"""
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            profit = trade.get('profit_loss', 0)
            is_win = profit > 0
            
            if streak_type == 'win' and is_win:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            elif streak_type == 'loss' and not is_win and profit != 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "core_metrics": {
                "expectancy": 0, "expectancy_r": 0, "average_r": 0, "median_r": 0,
                "std_dev_r": 0, "sharpe_ratio": 0, "profit_factor": 0, "payoff_ratio": 0,
                "win_rate": 0, "avg_win": 0, "avg_loss": 0, "largest_win": 0,
                "largest_loss": 0, "win_streak": 0, "loss_streak": 0
            },
            "distribution": {
                "histogram_data": [], "skewness": 0, "kurtosis": 0,
                "normality_test": None, "percentiles": {}
            },
            "rolling_analysis": {
                "rolling_expectancy": [], "rolling_win_rate": [],
                "rolling_r_multiple": [], "dates": [], "confidence_interval": {"lower": 0, "upper": 0}
            },
            "statistical_significance": {"significant": False, "t_statistic": 0, "p_value": 1},
            "edge_consistency": {"score": 0, "trend": "no_data"},
            "sample_size_warning": True,
            "reliability_score": 0
        }
def analyze_edge_quality(self, trades: List[Dict]) -> Dict[str, Any]:
    """Comprehensive edge quality analysis"""
    if not trades:
        return convert_numpy(self._empty_response())
    
    # ... your existing code ...
    
    result = {
        "core_metrics": core_metrics,
        "distribution": distribution,
        "rolling_analysis": rolling_analysis,
        "statistical_significance": significance,
        "edge_consistency": consistency,
        "sample_size_warning": len(trades) < 30,
        "reliability_score": self._calculate_reliability(trades)
    }
    
    return convert_numpy(result)
def analyze_edge_quality(self, trades: List[Dict]) -> Dict[str, Any]:
    """Comprehensive edge quality analysis"""
    if not trades:
        return convert_numpy(self._empty_response())
    
    # ... your existing code ...
    
    result = {
        "core_metrics": core_metrics,
        "distribution": distribution,
        "rolling_analysis": rolling_analysis,
        "statistical_significance": significance,
        "edge_consistency": consistency,
        "sample_size_warning": len(trades) < 30,
        "reliability_score": self._calculate_reliability(trades)
    }
    
    return convert_numpy(result)
