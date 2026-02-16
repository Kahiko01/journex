import requests
import json
from datetime import datetime, timedelta
import random

print("Fixing trade dates...")

# Get all trades
trades_response = requests.get('http://localhost:8000/api/v1/trades/')
trades = trades_response.json()

print(f"Found {len(trades)} trades")

# February dates mapping
feb_dates = [
    '2026-02-03', '2026-02-04', '2026-02-05', '2026-02-06', '2026-02-07',
    '2026-02-10', '2026-02-10', '2026-02-11', '2026-02-11', '2026-02-11',
    '2026-02-11', '2026-02-12', '2026-02-12', '2026-02-13', '2026-02-14'
]

# We need to update each trade with proper dates
# Note: The API might not have an update endpoint, so we'll need to delete and recreate

# First, let's check if we can update
for i, trade in enumerate(trades):
    trade_id = trade.get('id')
    if i < len(feb_dates):
        date_str = feb_dates[i]
        
        # Create proper ISO format dates
        hour = random.randint(9, 16)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        entry_time = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}"
        exit_time = f"{date_str}T{hour:02d}:{minute+15:02d}:{second:02d}"
        
        # Update trade with dates
        trade['entry_time'] = entry_time
        trade['exit_time'] = exit_time
        
        # Try to update via PUT (if endpoint exists)
        try:
            update_response = requests.put(f'http://localhost:8000/api/v1/trades/{trade_id}', json=trade)
            if update_response.status_code == 200:
                print(f"✅ Updated trade {trade_id} for {date_str}")
            else:
                print(f"❌ Failed to update trade {trade_id}: {update_response.status_code}")
        except:
            print(f"⚠️ Update failed for trade {trade_id}")

print("\nRefreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(refresh.json())

# Check calendar again
cal_response = requests.get('http://localhost:8000/api/v1/calendar/month/2026/2?user_id=1')
cal_data = cal_response.json()

days_count = 0
for week in cal_data.get('heatmap', []):
    for day in week:
        if not day.get('empty') and day.get('has_data'):
            days_count += 1
            print(f"📅 {day.get('date')}: {day.get('trades')} trades")

print(f"\nTotal days with trades: {days_count}")
