"""
Economic Calendar Service
Provides market events data
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class EconomicCalendarService:
    """Service for economic calendar events"""
    
    def __init__(self):
        self.events = self._generate_mock_events()
        logger.info(f"EconomicCalendarService initialized with {len(self.events)} events")
    
    def _generate_mock_events(self) -> List[Dict[str, Any]]:
        """Generate realistic mock economic events"""
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'NZD', 'CHF']
        impact_levels = ['Low', 'Medium', 'High']
        
        events = []
        start_date = datetime.now()
        
        # Event templates
        event_templates = [
            {"name": "Interest Rate Decision", "impact": "High"},
            {"name": "Non-Farm Payrolls", "impact": "High", "currency": "USD"},
            {"name": "CPI Inflation Data", "impact": "High"},
            {"name": "GDP Growth Rate", "impact": "High"},
            {"name": "Retail Sales", "impact": "Medium"},
            {"name": "Unemployment Rate", "impact": "Medium"},
            {"name": "Manufacturing PMI", "impact": "Medium"},
            {"name": "Services PMI", "impact": "Medium"},
            {"name": "Consumer Confidence", "impact": "Medium"},
            {"name": "Trade Balance", "impact": "Low"},
            {"name": "PPI Inflation", "impact": "Low"},
            {"name": "Building Permits", "impact": "Low"},
            {"name": "Housing Starts", "impact": "Low"},
            {"name": "Industrial Production", "impact": "Low"},
            {"name": "Central Bank Speech", "impact": "Medium"},
            {"name": "FOMC Minutes", "impact": "High", "currency": "USD"},
            {"name": "ECB Press Conference", "impact": "High", "currency": "EUR"},
            {"name": "BOE Inflation Report", "impact": "High", "currency": "GBP"},
            {"name": "BOJ Policy Statement", "impact": "High", "currency": "JPY"}
        ]
        
        # Generate events for the next 30 days
        for day_offset in range(30):
            date = start_date + timedelta(days=day_offset)
            
            # Generate 3-8 events per day
            num_events = random.randint(3, 8)
            
            for _ in range(num_events):
                template = random.choice(event_templates)
                currency = template.get('currency', random.choice(currencies))
                
                # Generate random time between 8:00 and 17:00
                hour = random.randint(8, 17)
                minute = random.choice([0, 15, 30, 45])
                
                event_time = date.replace(hour=hour, minute=minute, second=0)
                
                # Generate random actual/forecast/previous values based on impact
                if template['impact'] == 'High':
                    actual = round(random.uniform(-2, 2), 1)
                    forecast = round(random.uniform(-1, 1), 1)
                    previous = round(random.uniform(-1, 1), 1)
                elif template['impact'] == 'Medium':
                    actual = round(random.uniform(-1, 1), 1)
                    forecast = round(random.uniform(-0.5, 0.5), 1)
                    previous = round(random.uniform(-0.5, 0.5), 1)
                else:
                    actual = round(random.uniform(-0.5, 0.5), 1)
                    forecast = round(random.uniform(-0.3, 0.3), 1)
                    previous = round(random.uniform(-0.3, 0.3), 1)
                
                events.append({
                    'id': len(events) + 1,
                    'date': event_time.isoformat(),
                    'currency': currency,
                    'event': template['name'],
                    'impact': template['impact'],
                    'actual': actual,
                    'forecast': forecast,
                    'previous': previous,
                    'description': f"{currency} {template['name']}",
                    'is_relevant': random.choice([True, False])
                })
        
        return sorted(events, key=lambda x: x['date'])
    
    def get_events(self, currency: str = None, impact: str = None, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """Get economic events with filters"""
        filtered = self.events.copy()
        
        # Filter by currency
        if currency and currency != 'all':
            filtered = [e for e in filtered if e['currency'] == currency]
        
        # Filter by impact
        if impact and impact != 'all':
            filtered = [e for e in filtered if e['impact'] == impact]
        
        # Filter by date range
        if date_from:
            from_date = datetime.fromisoformat(date_from)
            filtered = [e for e in filtered if datetime.fromisoformat(e['date']) >= from_date]
        
        if date_to:
            to_date = datetime.fromisoformat(date_to)
            filtered = [e for e in filtered if datetime.fromisoformat(e['date']) <= to_date]
        
        return filtered
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """Get today's events"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        return [e for e in self.events if today <= datetime.fromisoformat(e['date']) < tomorrow]
    
    def get_upcoming_high_impact(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming high-impact events within X hours"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        return [
            e for e in self.events 
            if e['impact'] == 'High' 
            and now <= datetime.fromisoformat(e['date']) <= cutoff
        ]
    
    def mark_relevant(self, event_id: int, user_id: int, relevant: bool) -> Dict[str, Any]:
        """Mark an event as relevant for a user"""
        for event in self.events:
            if event['id'] == event_id:
                event['is_relevant'] = relevant
                return event
        return None
