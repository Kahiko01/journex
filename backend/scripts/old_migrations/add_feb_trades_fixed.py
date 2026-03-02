import requests
import json
from datetime import datetime, timedelta
import random

# Define trades directly in Python
trades = [
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
        "direction": "short",
        "entry_price": 1.2400,
        "exit_price": 1.2450,
        "stop_loss": 1.2350,
        "lot_size": 0.15,
        "strategy": "Breakout",
        "emotion": "Anxious",
        "rating": 2
    },
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
        "direction": "long",
        "entry_price": 0.6450,
        "exit_price": 0.6520,
        "stop_loss": 0.6420,
        "lot_size": 0.25,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 4
    },
    {
        "symbol": "USDCAD",
        "direction": "short",
        "entry_price": 1.3500,
        "exit_price": 1.3480,
        "stop_loss": 1.3520,
        "lot_size": 0.2,
        "strategy": "Scalping",
        "emotion": "Calm",
        "rating": 3
    },
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.0520,
        "exit_price": 1.0700,
        "stop_loss": 1.0480,
        "lot_size": 0.4,
        "strategy": "Swing",
        "emotion": "Confident",
        "rating": 5
    },
    {
        "symbol": "GBPUSD",
        "direction": "long",
        "entry_price": 1.2420,
        "exit_price": 1.2600,
        "stop_loss": 1.2380,
        "lot_size": 0.35,
        "strategy": "Swing",
        "emotion": "Confident",
        "rating": 5
    },
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.0530,
        "exit_price": 1.0535,
        "stop_loss": 1.0525,
        "lot_size": 0.1,
        "strategy": "Scalping",
        "emotion": "Greedy",
        "rating": 2
    },
    {
        "symbol": "EURUSD",
        "direction": "short",
        "entry_price": 1.0535,
        "exit_price": 1.0530,
        "stop_loss": 1.0540,
        "lot_size": 0.1,
        "strategy": "Scalping",
        "emotion": "Greedy",
        "rating": 2
    },
    {
        "symbol": "GBPUSD",
        "direction": "short",
        "entry_price": 1.2480,
        "exit_price": 1.2475,
        "stop_loss": 1.2490,
        "lot_size": 0.1,
        "strategy": "Scalping",
        "emotion": "Anxious",
        "rating": 2
    },
    {
        "symbol": "GBPUSD",
        "direction": "long",
        "entry_price": 1.2475,
        "exit_price": 1.2482,
        "stop_loss": 1.2465,
        "lot_size": 0.1,
        "strategy": "Scalping",
        "emotion": "Greedy",
        "rating": 2
    },
    {
        "symbol": "USDJPY",
        "direction": "long",
        "entry_price": 151.00,
        "exit_price": 152.00,
        "stop_loss": 150.50,
        "lot_size": 0.2,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 4
    },
    {
        "symbol": "AUDUSD",
        "direction": "long",
        "entry_price": 0.6480,
        "exit_price": 0.6530,
        "stop_loss": 0.6460,
        "lot_size": 0.2,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 4
    },
    {
        "symbol": "USDCAD",
        "direction": "long",
        "entry_price": 1.3520,
        "exit_price": 1.3460,
        "stop_loss": 1.3540,
        "lot_size": 0.3,
        "strategy": "FOMO",
        "emotion": "Greedy",
        "rating": 1
    },
    {
        "symbol": "EURUSD",
        "direction": "short",
        "entry_price": 1.0550,
        "exit_price": 1.0530,
        "stop_loss": 1.0570,
        "lot_size": 0.15,
        "strategy": "Scalping",
        "emotion": "Calm",
        "rating": 3
    }
]

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
    hour = random.randint(9, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    exit_minute = min(minute + random.randint(5, 60), 59)
    
    entry_time = f"{trade_date}T{hour:02d}:{minute:02d}:{second:02d}"
    exit_time = f"{trade_date}T{hour:02d}:{exit_minute:02d}:{second:02d}"
    
    trade['entry_time'] = entry_time
    trade['exit_time'] = exit_time
    
    # Send to API
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"✓ Added trade {i+1}: {trade['symbol']} on {trade_date}")
        else:
            print(f"✗ Failed to add trade {i+1}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error adding trade {i+1}: {e}")

print("\nAll trades attempted! Refreshing calendar...")

# Refresh calendar
try:
    refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
    print(refresh.json())
except Exception as e:
    print(f"Error refreshing calendar: {e}")
