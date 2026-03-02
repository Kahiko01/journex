import requests
import json
from datetime import datetime, timedelta
import random

print("=== ADDING TEST TRADES ===\n")

# Sample trades with different outcomes
trades = [
    # Winning trades
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.0500,
        "exit_price": 1.0650,
        "stop_loss": 1.0450,
        "lot_size": 0.2,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 5
    },
    {
        "symbol": "GBPUSD",
        "direction": "long",
        "entry_price": 1.2400,
        "exit_price": 1.2550,
        "stop_loss": 1.2350,
        "lot_size": 0.25,
        "strategy": "Breakout",
        "emotion": "Confident",
        "rating": 4
    },
    # Losing trades
    {
        "symbol": "USDJPY",
        "direction": "long",
        "entry_price": 150.50,
        "exit_price": 149.00,
        "stop_loss": 151.00,
        "lot_size": 0.3,
        "strategy": "Revenge",
        "emotion": "Greedy",
        "rating": 1
    },
    {
        "symbol": "AUDUSD",
        "direction": "short",
        "entry_price": 0.6500,
        "exit_price": 0.6550,
        "stop_loss": 0.6450,
        "lot_size": 0.2,
        "strategy": "Scalping",
        "emotion": "Anxious",
        "rating": 2
    },
    # Mixed day
    {
        "symbol": "USDCAD",
        "direction": "short",
        "entry_price": 1.3500,
        "exit_price": 1.3480,
        "stop_loss": 1.3520,
        "lot_size": 0.15,
        "strategy": "Scalping",
        "emotion": "Calm",
        "rating": 3
    },
    {
        "symbol": "EURUSD",
        "direction": "short",
        "entry_price": 1.0550,
        "exit_price": 1.0570,
        "stop_loss": 1.0530,
        "lot_size": 0.1,
        "strategy": "Scalping",
        "emotion": "Anxious",
        "rating": 2
    }
]

# February dates
feb_dates = [
    '2026-02-03', '2026-02-03',  # Two trades on Feb 3
    '2026-02-04', '2026-02-04',  # Two trades on Feb 4
    '2026-02-05', '2026-02-05'   # Two trades on Feb 5
]

print(f"Adding {len(trades)} trades...\n")

for i, trade in enumerate(trades):
    # Add entry and exit times
    date_str = feb_dates[i]
    
    # Randomize times within the day
    hour = random.randint(9, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    exit_minute = min(minute + random.randint(15, 60), 59)
    
    entry_time = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}"
    exit_time = f"{date_str}T{hour:02d}:{exit_minute:02d}:{second:02d}"
    
    trade['entry_time'] = entry_time
    trade['exit_time'] = exit_time
    
    # Send to API
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"  ✅ Added {trade['symbol']} on {date_str}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n✅ All trades added!")

# Refresh calendar
print("\n🔄 Refreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Calendar refresh result: {refresh.json()}")

print("\n=== DONE ===")
