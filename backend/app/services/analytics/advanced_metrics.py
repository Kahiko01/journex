"""
Advanced Trading Analytics Service
Production-grade metrics engine
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy import func, and_
from app.models.trade import Trade
import logging
from collections import defaultdict
import calendar

logger = logging.getLogger(__name__)

class AdvancedMetricsService:
    """Production-grade advanced analytics engine"""
    
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
        self.trades = self._fetch_trades()
        logger.info(f"AdvancedMetricsService initialized with {len(self.trades)} trades")
    
    def _fetch_trades(self) -> List[Trade]:
        """Optimized trade fetching with eager loading"""
        return self.db.query(Trade).filter(
            Trade.user_id == self.user_id
        ).order_by(Trade.exit_time).all()
    
    def calculate_core_metrics(self) -> Dict[str, Any]:
        """Core metrics with numerical stability"""
        if not self.trades:
            return self._empty_metrics()
        
        closed_trades = [t for t in self.trades if t.exit_price]
        winning = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
        losing = [t for t in closed_trades if t.profit_loss and t.profit_loss < 0]
        
        gross_profit = sum(t.profit_loss for t in winning)
        gross_loss = abs(sum(t.profit_loss for t in losing))
        
        return {
            "total_pl": round(sum(t.profit_loss or 0 for t in closed_trades), 2),
            "net_profit": round(sum(t.profit_loss or 0 for t in closed_trades), 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "win_rate": round((len(winning) / len(closed_trades) * 100), 2) if closed_trades else 0,
            "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0,
            "expectancy": round(np.mean([t.profit_loss or 0 for t in closed_trades]), 2) if closed_trades else 0,
            "avg_r": round(np.mean([t.r_multiple or 0 for t in closed_trades]), 2) if closed_trades else 0,
            "risk_reward": self._calculate_avg_risk_reward(winning, losing),
            "total_trades": len(closed_trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing)
        }
    
    def calculate_risk_metrics(self) -> Dict[str, Any]:
        """Advanced risk metrics with proper statistical methods"""
        if len(self.trades) < 5:
            return self._empty_risk_metrics()
        
        # Calculate daily returns for robust statistics
        daily_returns = self._calculate_daily_returns()
        if not daily_returns:
            return self._empty_risk_metrics()
        
        returns_array = np.array(daily_returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1)
        
        # Sharpe Ratio (annualized, assuming 252 trading days)
        sharpe = np.sqrt(252) * (mean_return / std_return) if std_return > 0 else 0
        
        # Sortino Ratio (downside deviation only)
        downside = returns_array[returns_array < 0]
        downside_std = np.std(downside) if len(downside) > 0 else 1
        sortino = np.sqrt(252) * (mean_return / downside_std) if downside_std > 0 else 0
        
        # Maximum Drawdown
        cumulative = np.cumsum(returns_array)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = abs(np.min(drawdown))
        max_drawdown_pct = (max_drawdown / np.max(running_max) * 100) if np.max(running_max) > 0 else 0
        
        # Calmar Ratio
        calmar = (mean_return * 252) / max_drawdown if max_drawdown > 0 else 0
        
        # Risk of Ruin (simplified Kelly-based)
        win_rate = len([t for t in self.trades if t.profit_loss and t.profit_loss > 0]) / len(self.trades)
        avg_win = np.mean([t.profit_loss for t in self.trades if t.profit_loss and t.profit_loss > 0]) or 0
        avg_loss = abs(np.mean([t.profit_loss for t in self.trades if t.profit_loss and t.profit_loss < 0])) or 1
        
        b = avg_win / avg_loss if avg_loss > 0 else 0
        kelly = win_rate - ((1 - win_rate) / b) if b > 0 else 0
        risk_of_ruin = ((1 - win_rate) / win_rate) ** (1 / b) if win_rate > 0.5 and b > 0 else 1.0
        
        # Value at Risk (VaR) and Conditional VaR
        var_95 = np.percentile(returns_array, 5)
        cvar_95 = returns_array[returns_array <= var_95].mean() if any(returns_array <= var_95) else var_95
        
        return {
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "calmar_ratio": round(calmar, 2),
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "risk_of_ruin": round(min(risk_of_ruin, 1.0), 4),
            "kelly_percentage": round(max(0, kelly), 4),
            "var_95": round(var_95, 2),
            "cvar_95": round(cvar_95, 2),
            "volatility": round(std_return * np.sqrt(252), 4),
            "downside_volatility": round(np.std(downside) * np.sqrt(252), 4) if len(downside) > 0 else 0
        }
    
    def calculate_rolling_metrics(self, window: int = 30) -> Dict[str, List]:
        """Calculate rolling metrics for trend analysis"""
        if len(self.trades) < window:
            return {"rolling_win_rate": [], "rolling_expectancy": []}
        
        sorted_trades = sorted(self.trades, key=lambda x: x.exit_time or x.created_at)
        rolling_win_rate = []
        rolling_expectancy = []
        dates = []
        
        for i in range(window, len(sorted_trades) + 1):
            window_trades = sorted_trades[i-window:i]
            wins = sum(1 for t in window_trades if t.profit_loss and t.profit_loss > 0)
            pls = [t.profit_loss or 0 for t in window_trades]
            
            rolling_win_rate.append(round(wins / window * 100, 2))
            rolling_expectancy.append(round(np.mean(pls), 2))
            dates.append(window_trades[-1].exit_time.isoformat() if window_trades[-1].exit_time else window_trades[-1].created_at.isoformat())
        
        return {
            "dates": dates,
            "rolling_win_rate": rolling_win_rate,
            "rolling_expectancy": rolling_expectancy
        }
    
    def calculate_mae_mfe(self) -> Dict[str, Any]:
        """Maximum Adverse/Favorable Excursion analysis"""
        if not self.trades:
            return {"mae_distribution": [], "mfe_distribution": []}
        
        # Safely get values, defaulting to empty list if attribute doesn't exist
        mae_values = []
        mfe_values = []
        
        for trade in self.trades:
            if hasattr(trade, 'mae') and trade.mae is not None:
                mae_values.append(trade.mae)
            if hasattr(trade, 'mfe') and trade.mfe is not None:
                mfe_values.append(trade.mfe)
        
        return {
            "mae_distribution": {
                "mean": round(np.mean(mae_values), 2) if mae_values else 0,
                "median": round(np.median(mae_values), 2) if mae_values else 0,
                "max": round(max(mae_values), 2) if mae_values else 0,
                "histogram": np.histogram(mae_values, bins=20)[0].tolist() if mae_values else []
            },
            "mfe_distribution": {
                "mean": round(np.mean(mfe_values), 2) if mfe_values else 0,
                "median": round(np.median(mfe_values), 2) if mfe_values else 0,
                "max": round(max(mfe_values), 2) if mfe_values else 0,
                "histogram": np.histogram(mfe_values, bins=20)[0].tolist() if mfe_values else []
            }
        }
    
    def calculate_time_analysis(self) -> Dict[str, Any]:
        """Time-in-trade and session analysis"""
        if not self.trades:
            return {}
        
        durations = []
        hour_performance = {i: {"trades": 0, "wins": 0, "pl": 0} for i in range(24)}
        
        for trade in self.trades:
            if trade.entry_time and trade.exit_time:
                duration = (trade.exit_time - trade.entry_time).total_seconds() / 60  # minutes
                durations.append(duration)
                
                hour = trade.entry_time.hour
                hour_performance[hour]["trades"] += 1
                if trade.profit_loss and trade.profit_loss > 0:
                    hour_performance[hour]["wins"] += 1
                if trade.profit_loss:
                    hour_performance[hour]["pl"] += trade.profit_loss
        
        return {
            "avg_trade_duration": round(np.mean(durations), 2) if durations else 0,
            "median_trade_duration": round(np.median(durations), 2) if durations else 0,
            "max_trade_duration": round(max(durations), 2) if durations else 0,
            "min_trade_duration": round(min(durations), 2) if durations else 0,
            "hourly_performance": [
                {
                    "hour": hour,
                    "trades": data["trades"],
                    "win_rate": round(data["wins"] / data["trades"] * 100, 2) if data["trades"] > 0 else 0,
                    "pl": round(data["pl"], 2)
                }
                for hour, data in hour_performance.items()
            ]
        }
    
    def get_calendar_heatmap(self, year: int, month: int) -> List[List[Dict]]:
        """Generate calendar heatmap with real trade data"""
        logger.info(f"Generating calendar for {year}-{month}")
        
        # Get trades for this month
        month_trades = []
        for trade in self.trades:
            if trade.exit_time and trade.exit_time.year == year and trade.exit_time.month == month:
                month_trades.append(trade)
        
        logger.info(f"Found {len(month_trades)} trades for {year}-{month}")
        
        # Group trades by day
        daily_stats = defaultdict(lambda: {'pl': 0, 'trades': 0, 'icons': []})
        
        for trade in month_trades:
            day = trade.exit_time.day
            daily_stats[day]['pl'] += trade.profit_loss or 0
            daily_stats[day]['trades'] += 1
            
            # Add icons for special conditions
            if trade.rating and trade.rating >= 4:
                if '⭐' not in daily_stats[day]['icons']:
                    daily_stats[day]['icons'].append('⭐')
            
            if trade.profit_loss and trade.profit_loss < -5000:
                if '⚠️' not in daily_stats[day]['icons']:
                    daily_stats[day]['icons'].append('⚠️')
        
        # Generate calendar grid
        cal = calendar.monthcalendar(year, month)
        heatmap = []
        
        # Find max absolute PL for color scaling
        all_pls = [stats['pl'] for stats in daily_stats.values()]
        max_abs_pl = max([abs(pl) for pl in all_pls] or [1])
        
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'empty': True})
                else:
                    stats = daily_stats.get(day, {'pl': 0, 'trades': 0, 'icons': []})
                    
                    # Determine color based on PL
                    if stats['trades'] == 0:
                        color = 'bg-gray-700'
                    elif stats['pl'] > 0:
                        intensity = min(1, stats['pl'] / max_abs_pl) if max_abs_pl > 0 else 0.5
                        if intensity > 0.7:
                            color = 'bg-green-700'
                        elif intensity > 0.3:
                            color = 'bg-green-600'
                        else:
                            color = 'bg-green-500'
                    else:
                        intensity = min(1, abs(stats['pl']) / max_abs_pl) if max_abs_pl > 0 else 0.5
                        if intensity > 0.7:
                            color = 'bg-red-700'
                        elif intensity > 0.3:
                            color = 'bg-red-600'
                        else:
                            color = 'bg-red-500'
                    
                    week_data.append({
                        'day': day,
                        'date': f"{year}-{month:02d}-{day:02d}",
                        'pl': round(stats['pl'], 2),
                        'trades': stats['trades'],
                        'color': color,
                        'icons': stats['icons'],
                        'has_data': stats['trades'] > 0
                    })
            heatmap.append(week_data)
        
        return heatmap
    
    def get_equity_curve_with_drawdown(self) -> List[Dict]:
        """Get equity curve with drawdown overlay for charts"""
        if not self.trades:
            return []
        
        sorted_trades = sorted([t for t in self.trades if t.exit_time], key=lambda x: x.exit_time)
        equity = 0
        peak = 0
        curve = []
        
        for trade in sorted_trades:
            equity += trade.profit_loss or 0
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            
            curve.append({
                'date': trade.exit_time.isoformat(),
                'equity': round(equity, 2),
                'peak': round(peak, 2),
                'drawdown': round(drawdown, 2)
            })
        
        return curve
    
    def get_r_multiple_distribution(self) -> Dict:
        """Get R-multiple distribution for histogram"""
        r_values = [t.r_multiple for t in self.trades if t.r_multiple]
        if not r_values:
            return {'bins': [], 'frequencies': []}
        
        bins = np.arange(-3, 3.5, 0.5)
        frequencies, _ = np.histogram(r_values, bins=bins)
        
        return {
            'bins': [f"{b:.1f}" for b in bins[:-1]],
            'frequencies': frequencies.tolist()
        }
    
    def get_performance_heatmap(self) -> Dict:
        """Get performance heatmap data"""
        # Simplified version - you can expand this
        return {"data": []}
    
    def get_risk_reward_scatter(self) -> Dict:
        """Get risk vs reward scatter plot data"""
        scatter_data = []
        for trade in self.trades:
            if trade.r_multiple and trade.profit_loss:
                scatter_data.append({
                    'risk': abs(trade.profit_loss) if trade.profit_loss < 0 else 0,
                    'reward': trade.profit_loss if trade.profit_loss > 0 else 0,
                    'r_multiple': trade.r_multiple
                })
        return {"scatter": scatter_data}
    
    def _calculate_daily_returns(self) -> List[float]:
        """Calculate daily returns for time-series analysis"""
        daily_pl = {}
        for trade in self.trades:
            if trade.exit_time and trade.profit_loss:
                date = trade.exit_time.date()
                daily_pl[date] = daily_pl.get(date, 0) + trade.profit_loss
        return list(daily_pl.values())
    
    def _calculate_avg_risk_reward(self, winning: List, losing: List) -> float:
        """Calculate average risk-reward ratio"""
        avg_win = np.mean([t.profit_loss for t in winning]) if winning else 0
        avg_loss = abs(np.mean([t.profit_loss for t in losing])) if losing else 1
        return round(avg_win / avg_loss, 2) if avg_loss > 0 else 0
    
    def _empty_metrics(self) -> Dict:
        return {
            "total_pl": 0, "net_profit": 0, "gross_profit": 0, "gross_loss": 0,
            "win_rate": 0, "profit_factor": 0, "expectancy": 0, "avg_r": 0,
            "risk_reward": 0, "total_trades": 0, "winning_trades": 0, "losing_trades": 0
        }
    
    def _empty_risk_metrics(self) -> Dict:
        return {
            "sharpe_ratio": 0, "sortino_ratio": 0, "calmar_ratio": 0,
            "max_drawdown": 0, "max_drawdown_pct": 0, "risk_of_ruin": 0,
            "kelly_percentage": 0, "var_95": 0, "cvar_95": 0,
            "volatility": 0, "downside_volatility": 0
        }
