"""
Advanced Trading Analytics Service
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict
import calendar
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    """Service for calculating advanced trading metrics"""
    
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
        self.trades = self._fetch_trades()
        logger.info(f"AdvancedAnalyticsService initialized with {len(self.trades)} trades for user {user_id}")
    
    def _fetch_trades(self) -> List[Dict]:
        """Fetch all closed trades for the user from database"""
        try:
            from app.models.trade import Trade
            from sqlalchemy import and_
            
            logger.info(f"Fetching trades for user {self.user_id} from database")
            
            # Query trades directly
            trades = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == self.user_id,
                    Trade.exit_time.isnot(None),
                    Trade.exit_price.isnot(None)
                )
            ).order_by(Trade.exit_time).all()
            
            logger.info(f"Found {len(trades)} closed trades in database")
            
            result = []
            for t in trades:
                trade_dict = {
                    'id': t.id,
                    'symbol': t.symbol,
                    'direction': t.direction,
                    'lot_size': float(t.lot_size) if t.lot_size else 0,
                    'entry_price': float(t.entry_price) if t.entry_price else 0,
                    'exit_price': float(t.exit_price) if t.exit_price else 0,
                    'profit_loss': float(t.profit_loss) if t.profit_loss else 0,
                    'r_multiple': float(t.r_multiple) if t.r_multiple else 0,
                    'strategy': t.strategy,
                    'entry_time': t.entry_time.isoformat() if t.entry_time else None,
                    'exit_time': t.exit_time.isoformat() if t.exit_time else None,
                    'stop_loss': float(t.stop_loss) if t.stop_loss else None,
                    'take_profit': float(t.take_profit) if t.take_profit else None,
                    'rating': t.rating,
                    'emotion': t.emotion,
                    'mistakes': t.mistakes or []
                }
                result.append(trade_dict)
            
            logger.info(f"Returning {len(result)} formatted trades")
            
            # Debug: print first few trades
            if result:
                logger.info("=== FIRST 5 TRADES ===")
                for i, trade in enumerate(result[:5]):
                    logger.info(f"Trade {i+1}: {trade['symbol']} - Exit: {trade['exit_time']} - P/L: {trade['profit_loss']}")
                logger.info("=====================")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get all dashboard metrics in one call"""
        return {
            'drawdown': self.get_drawdown_analysis(),
            'risk': self.get_risk_metrics(),
            'sessions': self.get_session_analysis(),
            'r_stats': self.get_r_multiple_stats()
        }
    
    def get_drawdown_analysis(self) -> Dict[str, Any]:
        """Calculate drawdown metrics"""
        if len(self.trades) < 2:
            return {
                'max_drawdown': 0,
                'max_drawdown_pct': 0,
                'avg_drawdown': 0,
                'current_drawdown': 0,
                'recovery_time': 0
            }
        
        # Calculate equity curve
        equity = 0
        peak = 0
        max_dd = 0
        max_dd_pct = 0
        dd_start = None
        max_duration = 0
        total_dd = 0
        dd_periods = 0
        
        # Sort trades by exit time
        sorted_trades = sorted([t for t in self.trades if t.get('exit_time')], 
                              key=lambda x: x['exit_time'])
        
        for trade in sorted_trades:
            equity += trade.get('profit_loss', 0)
            
            if equity > peak:
                peak = equity
                if dd_start is not None:
                    dd_start = None
            else:
                if dd_start is None:
                    dd_start = trade['exit_time']
                
                dd = peak - equity
                dd_pct = (dd / peak * 100) if peak > 0 else 0
                
                if dd > max_dd:
                    max_dd = dd
                    max_dd_pct = dd_pct
                
                total_dd += dd
                dd_periods += 1
        
        avg_dd = total_dd / dd_periods if dd_periods > 0 else 0
        
        return {
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_pct': round(max_dd_pct, 2),
            'avg_drawdown': round(avg_dd, 2),
            'current_drawdown': round(peak - equity, 2) if equity < peak else 0,
            'recovery_time': max_duration
        }
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Calculate risk metrics"""
        if not self.trades:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'avg_risk_per_trade': 0,
                'max_risk': 0,
                'risk_consistency': 0
            }
        
        # Calculate returns
        returns = [t.get('profit_loss', 0) for t in self.trades]
        positive_returns = [r for r in returns if r > 0]
        negative_returns = [r for r in returns if r < 0]
        
        # Sharpe ratio
        avg_return = np.mean(returns) if returns else 0
        std_return = np.std(returns) if returns else 1
        sharpe = avg_return / std_return if std_return != 0 else 0
        
        # Sortino ratio
        downside_std = np.std(negative_returns) if negative_returns else 1
        sortino = avg_return / downside_std if downside_std != 0 else 0
        
        # Risk per trade
        risk_amounts = [abs(t.get('profit_loss', 0)) for t in self.trades if t.get('profit_loss', 0) < 0]
        
        return {
            'sharpe_ratio': round(sharpe, 2),
            'sortino_ratio': round(sortino, 2),
            'avg_risk_per_trade': round(np.mean(risk_amounts), 2) if risk_amounts else 0,
            'max_risk': round(max(risk_amounts), 2) if risk_amounts else 0,
            'risk_consistency': 100  # Placeholder
        }
    
    def get_session_analysis(self) -> List[Dict[str, Any]]:
        """Analyze performance by trading session"""
        sessions = {
            'asia': {'name': 'Asia (00:00-08:00)', 'trades': 0, 'wins': 0, 'total_pl': 0, 'total_r': 0},
            'london': {'name': 'London (08:00-16:00)', 'trades': 0, 'wins': 0, 'total_pl': 0, 'total_r': 0},
            'ny': {'name': 'New York (16:00-00:00)', 'trades': 0, 'wins': 0, 'total_pl': 0, 'total_r': 0}
        }
        
        for trade in self.trades:
            if not trade.get('exit_time'):
                continue
            
            try:
                exit_time_str = trade['exit_time']
                if 'Z' in exit_time_str:
                    exit_time_str = exit_time_str.replace('Z', '+00:00')
                hour = datetime.fromisoformat(exit_time_str).hour
                
                if 0 <= hour < 8:
                    session = 'asia'
                elif 8 <= hour < 16:
                    session = 'london'
                else:
                    session = 'ny'
                
                sessions[session]['trades'] += 1
                sessions[session]['total_pl'] += trade.get('profit_loss', 0)
                if trade.get('r_multiple'):
                    sessions[session]['total_r'] += trade['r_multiple']
                if trade.get('profit_loss', 0) > 0:
                    sessions[session]['wins'] += 1
            except Exception as e:
                logger.error(f"Error parsing session for trade: {e}")
                continue
        
        result = []
        for session, data in sessions.items():
            if data['trades'] > 0:
                win_rate = (data['wins'] / data['trades'] * 100)
                avg_r = data['total_r'] / data['trades'] if data['trades'] > 0 else 0
                avg_pl = data['total_pl'] / data['trades'] if data['trades'] > 0 else 0
                
                result.append({
                    'name': data['name'],
                    'trades': data['trades'],
                    'win_rate': round(win_rate, 2),
                    'total_pl': round(data['total_pl'], 2),
                    'avg_pl': round(avg_pl, 2),
                    'avg_r': round(avg_r, 2)
                })
        
        return result
    
    def get_r_multiple_stats(self) -> Dict[str, Any]:
        """Calculate R-multiple statistics"""
        r_values = [t.get('r_multiple', 0) for t in self.trades if t.get('r_multiple')]
        
        if not r_values:
            return {
                'avg_r': 0,
                'median_r': 0,
                'max_r': 0,
                'min_r': 0,
                'positive_r': 0,
                'negative_r': 0,
                'expectancy': 0
            }
        
        positive_r = [r for r in r_values if r > 0]
        negative_r = [r for r in r_values if r < 0]
        
        return {
            'avg_r': round(np.mean(r_values), 2),
            'median_r': round(np.median(r_values), 2),
            'max_r': round(max(r_values), 2),
            'min_r': round(min(r_values), 2),
            'positive_r': len(positive_r),
            'negative_r': len(negative_r),
            'expectancy': round(np.mean(r_values), 2)
        }
    
    def get_calendar_heatmap(self, year: int, month: int) -> List[List[Dict]]:
        """Generate calendar heatmap with real trade data"""
        logger.info(f"Generating calendar for {year}-{month}")
        logger.info(f"Total trades available: {len(self.trades)}")
        
        # Log all trade dates for debugging
        all_dates = []
        for trade in self.trades:
            if trade.get('exit_time'):
                all_dates.append(trade['exit_time'][:10])
        logger.info(f"All trade dates: {sorted(set(all_dates))}")
        
        # Get trades for this month
        month_trades = []
        for trade in self.trades:
            if not trade.get('exit_time'):
                continue
            try:
                exit_time_str = trade['exit_time']
                if 'Z' in exit_time_str:
                    exit_time_str = exit_time_str.replace('Z', '+00:00')
                trade_date = datetime.fromisoformat(exit_time_str)
                if trade_date.year == year and trade_date.month == month:
                    month_trades.append(trade)
            except Exception as e:
                logger.error(f"Error parsing date for trade: {e}")
                continue
        
        logger.info(f"Found {len(month_trades)} trades for {year}-{month}")
        
        # Group trades by day
        daily_stats = defaultdict(lambda: {'pl': 0, 'trades': 0, 'icons': []})
        
        for trade in month_trades:
            exit_time_str = trade['exit_time']
            if 'Z' in exit_time_str:
                exit_time_str = exit_time_str.replace('Z', '+00:00')
            trade_date = datetime.fromisoformat(exit_time_str)
            day = trade_date.day
            
            daily_stats[day]['pl'] += trade.get('profit_loss', 0)
            daily_stats[day]['trades'] += 1
            
            # Add icons for special conditions
            if trade.get('rating') and trade.get('rating', 0) >= 4:
                if '⭐' not in daily_stats[day]['icons']:
                    daily_stats[day]['icons'].append('⭐')
            
            # Check for potential rule violations (large losses)
            if trade.get('profit_loss', 0) < -5000:
                if '⚠️' not in daily_stats[day]['icons']:
                    daily_stats[day]['icons'].append('⚠️')
        
        # Print daily stats for debugging
        days_with_trades = [day for day, stats in daily_stats.items() if stats['trades'] > 0]
        logger.info(f"Days with trades: {sorted(days_with_trades)}")
        
        # Generate calendar grid
        cal = calendar.monthcalendar(year, month)
        heatmap = []
        
        # Find max absolute PL for color scaling
        all_pls = [stats['pl'] for stats in daily_stats.values()]
        max_abs_pl = max([abs(pl) for pl in all_pls] or [1])
        logger.info(f"Max absolute P/L: {max_abs_pl}")
        
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
def _fetch_trades(self) -> List[Dict]:
    """Fetch all closed trades for the user from database"""
    try:
        from app.models.trade import Trade
        from sqlalchemy import and_
        
        logger.info(f"Fetching trades for user {self.user_id} from database")
        
        # Query trades directly
        trades = self.db.query(Trade).filter(
            and_(
                Trade.user_id == self.user_id,
                Trade.exit_time.isnot(None),
                Trade.exit_price.isnot(None)
            )
        ).order_by(Trade.exit_time).all()
        
        logger.info(f"Found {len(trades)} closed trades in database")
        
        result = []
        for t in trades:
            trade_dict = {
                'id': t.id,
                'symbol': t.symbol,
                'direction': t.direction,
                'lot_size': float(t.lot_size) if t.lot_size else 0,
                'entry_price': float(t.entry_price) if t.entry_price else 0,
                'exit_price': float(t.exit_price) if t.exit_price else 0,
                'profit_loss': float(t.profit_loss) if t.profit_loss else 0,
                'r_multiple': float(t.r_multiple) if t.r_multiple else 0,
                'strategy': t.strategy,
                'entry_time': t.entry_time.isoformat() if t.entry_time else None,
                'exit_time': t.exit_time.isoformat() if t.exit_time else None,
                'stop_loss': float(t.stop_loss) if t.stop_loss else None,
                'take_profit': float(t.take_profit) if t.take_profit else None,
                'rating': t.rating,
                'emotion': t.emotion,
                'mistakes': t.mistakes or []
            }
            result.append(trade_dict)
        
        logger.info(f"Returning {len(result)} formatted trades")
        
        # Debug: print first few trades
        if result:
            logger.info("=== FIRST 5 TRADES ===")
            for i, trade in enumerate(result[:5]):
                logger.info(f"Trade {i+1}: {trade['symbol']} - Exit: {trade['exit_time']} - P/L: {trade['profit_loss']}")
            logger.info("=====================")
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        logger.error(traceback.format_exc())
        return []
