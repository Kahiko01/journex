"""
Mathematical Formulas for Advanced Trading Analytics
All formulas are production-ready with proper error handling
"""

import numpy as np
from typing import List, Dict, Any, Optional
import math

class TradingFormulas:
    
    @staticmethod
    def calculate_expectancy(trades: List[Dict]) -> float:
        """
        E = (Win Rate × Average Win) - (Loss Rate × Average Loss)
        """
        if not trades:
            return 0.0
        
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        if not winning_trades or not losing_trades:
            return 0.0
        
        win_rate = len(winning_trades) / len(trades)
        loss_rate = len(losing_trades) / len(trades)
        
        avg_win = np.mean([t['profit_loss'] for t in winning_trades])
        avg_loss = abs(np.mean([t['profit_loss'] for t in losing_trades]))
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        return round(expectancy, 2)
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Sharpe Ratio = (Rp - Rf) / σp
        Where Rp = portfolio return, Rf = risk-free rate, σp = standard deviation
        """
        if len(returns) < 2:
            return 0.0
        
        avg_return = np.mean(returns)
        std_dev = np.std(returns)
        
        if std_dev == 0:
            return 0.0
        
        sharpe = (avg_return - risk_free_rate/252) / std_dev * math.sqrt(252)
        return round(sharpe, 2)
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Sortino Ratio = (Rp - Rf) / σd
        Where σd = downside deviation (only negative returns)
        """
        if len(returns) < 2:
            return 0.0
        
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return float('inf') if np.mean(returns) > 0 else 0.0
        
        downside_std = np.std(negative_returns)
        if downside_std == 0:
            return 0.0
        
        avg_return = np.mean(returns)
        sortino = (avg_return - risk_free_rate/252) / downside_std * math.sqrt(252)
        return round(sortino, 2)
    
    @staticmethod
    def calculate_calmar_ratio(returns: List[float], max_drawdown_pct: float) -> float:
        """
        Calmar Ratio = Annualized Return / Max Drawdown
        """
        if max_drawdown_pct == 0:
            return 0.0
        
        annualized_return = np.mean(returns) * 252
        calmar = annualized_return / abs(max_drawdown_pct)
        return round(calmar, 2)
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """
        Profit Factor = Gross Profit / Gross Loss
        """
        gross_profit = sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) > 0)
        gross_loss = abs(sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    @staticmethod
    def calculate_payoff_ratio(trades: List[Dict]) -> float:
        """
        Payoff Ratio = Average Win / Average Loss
        """
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        if not winning_trades or not losing_trades:
            return 0.0
        
        avg_win = np.mean([t['profit_loss'] for t in winning_trades])
        avg_loss = abs(np.mean([t['profit_loss'] for t in losing_trades]))
        
        if avg_loss == 0:
            return float('inf')
        
        return round(avg_win / avg_loss, 2)
    
    @staticmethod
    def calculate_kelly_percentage(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Kelly % = W - [(1-W)/R]
        Where W = Win Rate, R = Win/Loss Ratio
        """
        if avg_loss == 0:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        return max(0, round(kelly * 100, 2))  # Return as percentage
    
    @staticmethod
    def calculate_risk_of_ruin(win_rate: float, risk_per_trade: float, account_size: float) -> float:
        """
        Risk of Ruin = ((1 - Edge) / (1 + Edge)) ^ Number of Trades
        Simplified version
        """
        if win_rate <= 0.5:
            return 1.0
        
        edge = win_rate - 0.5
        ruin_probability = ((1 - edge) / (1 + edge)) ** (account_size / (risk_per_trade * account_size))
        return round(ruin_probability * 100, 2)
    
    @staticmethod
    def calculate_consistency_index(returns: List[float]) -> float:
        """
        Consistency Index = % of positive periods / volatility
        Higher is better
        """
        if not returns:
            return 0.0
        
        positive_periods = len([r for r in returns if r > 0])
        positive_ratio = positive_periods / len(returns)
        
        volatility = np.std(returns) if len(returns) > 1 else 1
        
        if volatility == 0:
            return positive_ratio * 100
        
        consistency = (positive_ratio / volatility) * 100
        return round(consistency, 2)
    
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """
        Value at Risk (VaR) at given confidence level
        """
        if len(returns) < 2:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return round(sorted_returns[index], 2)
    
    @staticmethod
    def calculate_cvar(returns: List[float], confidence_level: float = 0.95) -> float:
        """
        Conditional VaR (Expected Shortfall)
        """
        if len(returns) < 2:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        tail_returns = sorted_returns[:index]
        
        if not tail_returns:
            return sorted_returns[0]
        
        return round(np.mean(tail_returns), 2)
    
    @staticmethod
    def calculate_drawdown_efficiency(trades: List[Dict], max_drawdown: float) -> float:
        """
        Drawdown Efficiency = Total Return / Max Drawdown
        Measures return per unit of drawdown risk
        """
        total_return = sum(t.get('profit_loss', 0) for t in trades)
        
        if max_drawdown == 0:
            return float('inf') if total_return > 0 else 0.0
        
        return round(total_return / abs(max_drawdown), 2)
