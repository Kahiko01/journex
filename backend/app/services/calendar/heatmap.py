from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

class HeatmapService:
    def __init__(self):
        self.color_intensity = {
            'very_high_profit': 'bg-green-700',
            'high_profit': 'bg-green-600',
            'medium_profit': 'bg-green-500',
            'low_profit': 'bg-green-400',
            'no_trades': 'bg-gray-700',
            'low_loss': 'bg-red-400',
            'medium_loss': 'bg-red-500',
            'high_loss': 'bg-red-600',
            'very_high_loss': 'bg-red-700'
        }
    
    def get_color_for_pl(self, pl: float, max_abs_pl: float) -> str:
        """Determine cell color based on P/L intensity"""
        if pl == 0:
            return self.color_intensity['no_trades']
        
        # Normalize P/L to intensity (0-1)
        intensity = min(1, abs(pl) / max_abs_pl) if max_abs_pl > 0 else 0.5
        
        if pl > 0:
            if intensity > 0.75:
                return self.color_intensity['very_high_profit']
            elif intensity > 0.5:
                return self.color_intensity['high_profit']
            elif intensity > 0.25:
                return self.color_intensity['medium_profit']
            else:
                return self.color_intensity['low_profit']
        else:
            if intensity > 0.75:
                return self.color_intensity['very_high_loss']
            elif intensity > 0.5:
                return self.color_intensity['high_loss']
            elif intensity > 0.25:
                return self.color_intensity['medium_loss']
            else:
                return self.color_intensity['low_loss']
    
    def generate_month_heatmap(self, year: int, month: int, daily_data: Dict[str, Any]) -> List[List[Dict]]:
        """Generate heatmap grid for a month"""
        cal = calendar.monthcalendar(year, month)
        heatmap = []
        
        # Find max absolute P/L for scaling colors
        max_abs_pl = max([abs(d.get('total_pl', 0)) for d in daily_data.values()] or [1])
        
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'empty': True})
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    day_info = daily_data.get(date_str, {})
                    
                    # Determine color
                    color = self.get_color_for_pl(day_info.get('total_pl', 0), max_abs_pl)
                    
                    # Determine icons
                    icons = []
                    if day_info.get('rule_violations', 0) > 0:
                        icons.append('⚠')
                    if day_info.get('overtrading_detected', False):
                        icons.append('🔥')
                    if day_info.get('high_rated_trades', 0) > 0:
                        icons.append('⭐')
                    if day_info.get('max_drawdown_spike', False):
                        icons.append('📉')
                    
                    week_data.append({
                        'day': day,
                        'date': date_str,
                        'pl': day_info.get('total_pl', 0),
                        'trades': day_info.get('total_trades', 0),
                        'win_rate': day_info.get('win_rate', 0),
                        'sum_r': day_info.get('sum_r_multiple', 0),
                        'color': color,
                        'icons': icons,
                        'discipline_score': day_info.get('discipline_score', 100),
                        'has_data': bool(day_info)
                    })
            heatmap.append(week_data)
        
        return heatmap
    
    def generate_year_heatmap(self, year: int, yearly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate GitHub-style year heatmap"""
        months = []
        max_abs_pl = max([abs(d.get('total_pl', 0)) for d in yearly_data.values()] or [1])
        
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            month_days = []
            
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_info = yearly_data.get(date_str, {})
                
                color = self.get_color_for_pl(day_info.get('total_pl', 0), max_abs_pl)
                
                month_days.append({
                    'date': date_str,
                    'pl': day_info.get('total_pl', 0),
                    'color': color,
                    'has_data': bool(day_info)
                })
            
            months.append({
                'name': month_name,
                'days': month_days
            })
        
        return {'months': months}
    
    def get_tooltip_data(self, day_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hover tooltip content"""
        return {
            'total_risk': day_data.get('total_risk_taken', 0),
            'largest_win': day_data.get('largest_win', 0),
            'largest_loss': day_data.get('largest_loss', 0),
            'avg_rr': day_data.get('avg_rr', 0),
            'sessions': {
                'asia': {'trades': day_data.get('asia_trades', 0), 'pl': day_data.get('asia_pl', 0)},
                'london': {'trades': day_data.get('london_trades', 0), 'pl': day_data.get('london_pl', 0)},
                'ny': {'trades': day_data.get('ny_trades', 0), 'pl': day_data.get('ny_pl', 0)}
            },
            'strategies': day_data.get('strategy_performance', {}),
            'emotions': day_data.get('emotions', {})
        }
