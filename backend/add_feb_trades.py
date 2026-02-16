import requests
import json
from datetime import datetime, timedelta

# Load trades
with open('feb_trades.json', 'r') as f:
    trades = json.load(f)

# February 2026 dates
feb_dates = [
    '2026-02-03',  # Tuesday
    '2026-02-04',  # Wednesday
    '2026-02-05',  # Thursday
    '2026-02-06',  # Friday
    '2026-02-07',  # Saturday
    '2026-02-10',  # Tuesday
    '2026-02-10',  # Tuesday (second trade)
    '2026-02-11',  # Wednesday
    '2026-02-11',  # Wednesday
    '2026-02-11',  # Wednesday
    '2026-02-11',  # Wednesday
    '2026-02-12',  # Thursday
    '2026-02-12',  # Thursday
    '2026-02-13',  # Friday
    '2026-02-14',  # Saturday
]

print(f"Adding {len(trades)} trades to February calendar...")

for i, trade in enumerate(trades):
    # Add entry and exit times
    trade_date = feb_dates[i]
    
    # Randomize times within the day
    import random
    hour = random.randint(9, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    entry_time = f"{trade_date}T{hour:02d}:{minute:02d}:{second:02d}"
    exit_time = f"{trade_date}T{hour:02d}:{minute+random.randint(1,59):02d}:{second:02d}"
    
    trade['entry_time'] = entry_time
    trade['exit_time'] = exit_time
    
    # Send to API
    response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
    if response.status_code == 200:
        print(f"✓ Added trade {i+1}: {trade['symbol']} on {trade_date}")
    else:
        print(f"✗ Failed to add trade {i+1}: {response.text}")

print("\nAll trades added! Refreshing calendar...")

# Refresh calendar
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(refresh.json())
