import requests
import json

print("=== ADDING TRADES DIRECTLY ===\n")

# Define trades directly in Python (no JSON file needed)
trades = [
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.05,
        "exit_price": 1.065,
        "stop_loss": 1.045,
        "lot_size": 0.2,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 5,
        "entry_time": "2026-02-03T10:30:00",
        "exit_time": "2026-02-03T15:45:00"
    },
    {
        "symbol": "GBPUSD",
        "direction": "short",
        "entry_price": 1.24,
        "exit_price": 1.245,
        "stop_loss": 1.235,
        "lot_size": 0.15,
        "strategy": "Breakout",
        "emotion": "Anxious",
        "rating": 2,
        "entry_time": "2026-02-04T09:15:00",
        "exit_time": "2026-02-04T11:30:00"
    },
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.052,
        "exit_price": 1.07,
        "stop_loss": 1.048,
        "lot_size": 0.4,
        "strategy": "Swing",
        "emotion": "Confident",
        "rating": 5,
        "entry_time": "2026-02-10T13:20:00",
        "exit_time": "2026-02-10T16:45:00"
    },
    {
        "symbol": "USDJPY",
        "direction": "long",
        "entry_price": 150.5,
        "exit_price": 152.0,
        "stop_loss": 149.5,
        "lot_size": 0.25,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 4,
        "entry_time": "2026-02-06T14:00:00",
        "exit_time": "2026-02-06T16:30:00"
    },
    {
        "symbol": "AUDUSD",
        "direction": "short",
        "entry_price": 0.655,
        "exit_price": 0.65,
        "stop_loss": 0.658,
        "lot_size": 0.3,
        "strategy": "Breakout",
        "emotion": "Anxious",
        "rating": 2,
        "entry_time": "2026-02-11T11:00:00",
        "exit_time": "2026-02-11T14:15:00"
    },
    {
        "symbol": "USDCAD",
        "direction": "long",
        "entry_price": 1.35,
        "exit_price": 1.36,
        "stop_loss": 1.345,
        "lot_size": 0.2,
        "strategy": "Trend Following",
        "emotion": "Calm",
        "rating": 4,
        "entry_time": "2026-02-12T10:00:00",
        "exit_time": "2026-02-12T15:30:00"
    },
    {
        "symbol": "GBPUSD",
        "direction": "long",
        "entry_price": 1.245,
        "exit_price": 1.255,
        "stop_loss": 1.24,
        "lot_size": 0.25,
        "strategy": "Breakout",
        "emotion": "Confident",
        "rating": 4,
        "entry_time": "2026-02-13T13:00:00",
        "exit_time": "2026-02-13T16:15:00"
    },
    {
        "symbol": "EURUSD",
        "direction": "short",
        "entry_price": 1.055,
        "exit_price": 1.048,
        "stop_loss": 1.058,
        "lot_size": 0.3,
        "strategy": "Reversal",
        "emotion": "Calm",
        "rating": 3,
        "entry_time": "2026-02-14T09:30:00",
        "exit_time": "2026-02-14T12:45:00"
    }
]

print(f"Prepared {len(trades)} trades to add\n")

# Add each trade
success_count = 0
for i, trade in enumerate(trades):
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"✅ Added trade {i+1}: {trade['symbol']} on {trade['entry_time'][:10]}")
            success_count += 1
        else:
            print(f"❌ Failed to add trade {i+1}: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error adding trade {i+1}: {e}")

print(f"\n✅ Successfully added {success_count} out of {len(trades)} trades")

# Refresh calendar
print("\n🔄 Refreshing calendar...")
try:
    refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
    print(f"Calendar refresh result: {refresh.json()}")
except Exception as e:
    print(f"Error refreshing calendar: {e}")

print("\n=== DONE ===")
