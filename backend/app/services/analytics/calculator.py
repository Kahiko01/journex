from typing import List, Dict, Any
from datetime import datetime
import numpy as np

class AnalyticsCalculator:
    
    @staticmethod
    def calculate_drawdown(trades: List[Dict]) -> Dict[str, Any]:
        """Calculate drawdown metrics"""
        if not trades:
            return {
                "max_drawdown": 0,
                "max_drawdown_pct": 0,
                "avg_drawdown": 0,
                "current_drawdown": 0,
                "recovery_time": 0
            }
        
        # Sort trades by exit time
        closed_trades = [t for t in trades if t.get('exit_time') and t.get('exit_price')]
        closed_trades.sort(key=lambda x: x['exit_time'])
        
        equity_curve = []
        running_pl = 0
        peak = 0
        max_drawdown = 0
        max_drawdown_pct = 0
        drawdown_start = None
        longest_recovery = 0
        current_recovery = 0
        
        for trade in closed_trades:
            # Calculate P/L
            if trade['direction'] == 'long':
                pl = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
            else:
                pl = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
            
            running_pl += pl
            equity_curve.append(running_pl)
            
            # Update peak
            if running_pl > peak:
                peak = running_pl
                if drawdown_start is not None:
                    # Recovery happened
                    recovery_time = len(equity_curve) - drawdown_start
                    if recovery_time > longest_recovery:
                        longest_recovery = recovery_time
                    drawdown_start = None
            else:
                # In drawdown
                if drawdown_start is None:
                    drawdown_start = len(equity_curve) - 1
                
                drawdown = peak - running_pl
                drawdown_pct = (drawdown / peak * 100) if peak > 0 else 0
                
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                if drawdown_pct > max_drawdown_pct:
                    max_drawdown_pct = drawdown_pct
        
        # Calculate average drawdown
        total_drawdown = 0
        drawdown_periods = 0
        for i in range(1, len(equity_curve)):
            if equity_curve[i] < equity_curve[i-1]:
                total_drawdown += (equity_curve[i-1] - equity_curve[i])
                drawdown_periods += 1
        
        avg_drawdown = total_drawdown / drawdown_periods if drawdown_periods > 0 else 0
        
        return {
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "avg_drawdown": round(avg_drawdown, 2),
            "current_drawdown": round(peak - running_pl, 2) if running_pl < peak else 0,
            "longest_recovery": longest_recovery
        }
    
    @staticmethod
    def calculate_risk_metrics(trades: List[Dict]) -> Dict[str, Any]:
        """Calculate risk metrics including Sharpe and Sortino ratios"""
        if len(trades) < 2:
            return {
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "avg_risk_per_trade": 0,
                "max_risk": 0,
                "risk_consistency": 100
            }
        
        # Calculate returns for each trade
        returns = []
        for trade in trades:
            if trade.get('exit_price'):
                if trade['direction'] == 'long':
                    ret = (trade['exit_price'] - trade['entry_price']) / trade['entry_price']
                else:
                    ret = (trade['entry_price'] - trade['exit_price']) / trade['entry_price']
                returns.append(ret * 100)  # Convert to percentage
        
        if not returns:
            return {}
        
        # Calculate metrics
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        negative_returns = [r for r in returns if r < 0]
        downside_std = np.std(negative_returns) if negative_returns else 1
        
        # Sharpe ratio (assuming risk-free rate of 0)
        sharpe = avg_return / std_return if std_return > 0 else 0
        
        # Sortino ratio (uses downside deviation)
        sortino = avg_return / downside_std if downside_std > 0 else 0
        
        # Risk per trade
        risk_per_trade = []
        for trade in trades:
            if trade.get('stop_loss') and trade.get('entry_price'):
                if trade['direction'] == 'long':
                    risk = abs(trade['entry_price'] - trade['stop_loss']) * trade['lot_size']
                else:
                    risk = abs(trade['stop_loss'] - trade['entry_price']) * trade['lot_size']
                risk_per_trade.append(risk)
        
        avg_risk = np.mean(risk_per_trade) if risk_per_trade else 0
        
        # Risk consistency (coefficient of variation)
        if risk_per_trade and np.mean(risk_per_trade) > 0:
            cv = np.std(risk_per_trade) / np.mean(risk_per_trade)
            consistency = max(0, 100 - (cv * 50))
        else:
            consistency = 100
        
        return {
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "avg_risk_per_trade": round(avg_risk, 2),
            "max_risk": round(max(risk_per_trade) if risk_per_trade else 0, 2),
            "risk_consistency": round(consistency, 2),
            "total_returns": round(sum(returns), 2),
            "avg_return": round(avg_return, 2),
            "volatility": round(std_return, 2)
        }
    
    @staticmethod
    def analyze_sessions(trades: List[Dict]) -> List[Dict]:
        """Analyze performance by trading session"""
        sessions = {
            "asia": {"name": "Asia", "trades": 0, "wins": 0, "total_pl": 0, "total_r": 0},
            "london": {"name": "London", "trades": 0, "wins": 0, "total_pl": 0, "total_r": 0},
            "ny": {"name": "New York", "trades": 0, "wins": 0, "total_pl": 0, "total_r": 0}
        }
        
        for trade in trades:
            if not trade.get('exit_time'):
                continue
            
            # Parse the hour from exit_time
            try:
                exit_time = trade['exit_time']
                if isinstance(exit_time, str):
                    if 'T' in exit_time:
                        hour = int(exit_time.split('T')[1].split(':')[0])
                    else:
                        continue
                else:
                    continue
                
                # Determine session based on hour (simplified)
                # Asia: 0-8, London: 8-16, NY: 16-24
                if 0 <= hour < 8:
                    session = "asia"
                elif 8 <= hour < 16:
                    session = "london"
                else:
                    session = "ny"
                
                # Calculate P/L
                if trade['direction'] == 'long':
                    pl = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
                else:
                    pl = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
                
                sessions[session]["trades"] += 1
                sessions[session]["total_pl"] += pl
                sessions[session]["total_r"] += trade.get('r_multiple', 0)
                
                if pl > 0:
                    sessions[session]["wins"] += 1
                    
            except Exception:
                continue
        
        # Calculate metrics for each session
        result = []
        for session, data in sessions.items():
            if data["trades"] > 0:
                win_rate = (data["wins"] / data["trades"]) * 100
                avg_pl = data["total_pl"] / data["trades"]
                avg_r = data["total_r"] / data["trades"]
                
                result.append({
                    "name": data["name"],
                    "trades": data["trades"],
                    "win_rate": round(win_rate, 1),
                    "total_pl": round(data["total_pl"], 2),
                    "avg_pl": round(avg_pl, 2),
                    "avg_r": round(avg_r, 2)
                })
        
        return result
    
    @staticmethod
    def calculate_r_multiple_stats(trades: List[Dict]) -> Dict[str, Any]:
        """Calculate R-multiple statistics"""
        r_values = [t.get('r_multiple', 0) for t in trades if t.get('r_multiple')]
        
        if not r_values:
            return {
                "avg_r": 0,
                "median_r": 0,
                "max_r": 0,
                "min_r": 0,
                "positive_r": 0,
                "negative_r": 0,
                "expectancy": 0
            }
        
        positive_r = [r for r in r_values if r > 0]
        negative_r = [r for r in r_values if r < 0]
        
        return {
            "avg_r": round(np.mean(r_values), 2),
            "median_r": round(np.median(r_values), 2),
            "max_r": round(max(r_values), 2),
            "min_r": round(min(r_values), 2),
            "positive_r": len(positive_r),
            "negative_r": len(negative_r),
            "expectancy": round(np.mean(r_values), 2)
        }
