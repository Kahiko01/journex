import requests
import json
from datetime import datetime, timedelta
import random

print("=== FIXING TRADES FOR CALENDAR ===\n")

# Get all trades
response = requests.get('http://localhost:8000/api/v1/trades/')
trades = response.json()
print(f"Found {len(trades)} trades\n")

if len(trades) == 0:
    print("❌ No trades found! Please add some trades first.")
    exit()

# February dates for the trades (assign each trade to a day in Feb)
feb_dates = [
    '2026-02-03', '2026-02-03', '2026-02-04', '2026-02-04', '2026-02-05',
    '2026-02-06', '2026-02-06', '2026-02-07', '2026-02-10', '2026-02-10',
    '2026-02-11', '2026-02-11', '2026-02-11', '2026-02-12', '2026-02-12',
    '2026-02-13', '2026-02-13', '2026-02-14', '2026-02-14', '2026-02-14'
]

print("⚠️  We need to delete and recreate trades with proper dates")
print("Deleting all trades...")

# Delete all trades
for trade in trades:
    trade_id = trade['id']
    delete_response = requests.delete(f'http://localhost:8000/api/v1/trades/{trade_id}')
    if delete_response.status_code == 200:
        print(f"  ✅ Deleted trade {trade_id}")
    else:
        print(f"  ❌ Failed to delete trade {trade_id}")

print("\n✅ All trades deleted")

# Recreate trades with proper dates
print("\n🔄 Recreating trades with proper exit times...")

# Sample trades data
sample_trades = [
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0500, "exit_price": 1.0650, "stop_loss": 1.0450, "lot_size": 0.2, "strategy": "Trend Following", "emotion": "Calm", "rating": 5},
    {"symbol": "GBPUSD", "direction": "short", "entry_price": 1.2400, "exit_price": 1.2350, "stop_loss": 1.2450, "lot_size": 0.15, "strategy": "Breakout", "emotion": "Anxious", "rating": 2},
    {"symbol": "USDJPY", "direction": "long", "entry_price": 150.50, "exit_price": 149.00, "stop_loss": 151.00, "lot_size": 0.3, "strategy": "Revenge", "emotion": "Greedy", "rating": 1},
    {"symbol": "AUDUSD", "direction": "long", "entry_price": 0.6450, "exit_price": 0.6520, "stop_loss": 0.6420, "lot_size": 0.25, "strategy": "Trend Following", "emotion": "Calm", "rating": 4},
    {"symbol": "USDCAD", "direction": "short", "entry_price": 1.3500, "exit_price": 1.3480, "stop_loss": 1.3520, "lot_size": 0.2, "strategy": "Scalping", "emotion": "Calm", "rating": 3},
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0520, "exit_price": 1.0700, "stop_loss": 1.0480, "lot_size": 0.4, "strategy": "Swing", "emotion": "Confident", "rating": 5},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2420, "exit_price": 1.2600, "stop_loss": 1.2380, "lot_size": 0.35, "strategy": "Swing", "emotion": "Confident", "rating": 5},
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0530, "exit_price": 1.0535, "stop_loss": 1.0525, "lot_size": 0.1, "strategy": "Scalping", "emotion": "Greedy", "rating": 2},
    {"symbol": "EURUSD", "direction": "short", "entry_price": 1.0535, "exit_price": 1.0530, "stop_loss": 1.0540, "lot_size": 0.1, "strategy": "Scalping", "emotion": "Greedy", "rating": 2},
    {"symbol": "GBPUSD", "direction": "short", "entry_price": 1.2480, "exit_price": 1.2475, "stop_loss": 1.2490, "lot_size": 0.1, "strategy": "Scalping", "emotion": "Anxious", "rating": 2},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2475, "exit_price": 1.2482, "stop_loss": 1.2465, "lot_size": 0.1, "strategy": "Scalping", "emotion": "Greedy", "rating": 2},
    {"symbol": "USDJPY", "direction": "long", "entry_price": 151.00, "exit_price": 152.00, "stop_loss": 150.50, "lot_size": 0.2, "strategy": "Trend Following", "emotion": "Calm", "rating": 4},
    {"symbol": "AUDUSD", "direction": "long", "entry_price": 0.6480, "exit_price": 0.6530, "stop_loss": 0.6460, "lot_size": 0.2, "strategy": "Trend Following", "emotion": "Calm", "rating": 4},
    {"symbol": "USDCAD", "direction": "long", "entry_price": 1.3520, "exit_price": 1.3460, "stop_loss": 1.3540, "lot_size": 0.3, "strategy": "FOMO", "emotion": "Greedy", "rating": 1},
    {"symbol": "EURUSD", "direction": "short", "entry_price": 1.0550, "exit_price": 1.0530, "stop_loss": 1.0570, "lot_size": 0.15, "strategy": "Scalping", "emotion": "Calm", "rating": 3},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2450, "exit_price": 1.2550, "stop_loss": 1.2400, "lot_size": 0.25, "strategy": "Breakout", "emotion": "Confident", "rating": 4},
    {"symbol": "USDJPY", "direction": "short", "entry_price": 151.50, "exit_price": 150.50, "stop_loss": 152.00, "lot_size": 0.2, "strategy": "Breakout", "emotion": "Calm", "rating": 4},
    {"symbol": "AUDUSD", "direction": "short", "entry_price": 0.6500, "exit_price": 0.6470, "stop_loss": 0.6530, "lot_size": 0.15, "strategy": "Scalping", "emotion": "Anxious", "rating": 2},
    {"symbol": "USDCAD", "direction": "short", "entry_price": 1.3550, "exit_price": 1.3520, "stop_loss": 1.3570, "lot_size": 0.2, "strategy": "Scalping", "emotion": "Calm", "rating": 3},
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0540, "exit_price": 1.0580, "stop_loss": 1.0520, "lot_size": 0.3, "strategy": "Trend Following", "emotion": "Calm", "rating": 4}
]

# Use only as many trades as we have dates
for i in range(min(len(sample_trades), len(feb_dates))):
    trade = sample_trades[i]
    date_str = feb_dates[i]
    
    # Create proper ISO format dates with random times
    hour = random.randint(9, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    exit_minute = min(minute + random.randint(15, 120), 59)
    
    entry_time = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}"
    exit_time = f"{date_str}T{hour:02d}:{exit_minute:02d}:{second:02d}"
    
    # Add the times to the trade
    trade['entry_time'] = entry_time
    trade['exit_time'] = exit_time
    
    # Send to API
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"  ✅ Added trade {i+1}: {trade['symbol']} on {date_str}")
        else:
            print(f"  ❌ Failed to add trade {i+1}: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error adding trade {i+1}: {e}")

# Refresh calendar
print("\n🔄 Refreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Calendar refresh result: {refresh.json()}")

print("\n=== DONE ===")
