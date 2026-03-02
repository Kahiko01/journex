import requests
import json

print("=== ADDING PROPER FEBRUARY TRADES ===\n")

trades = [
    # Feb 3 - Winning day (2 trades)
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0500, "exit_price": 1.0650, "lot_size": 0.2, "entry_time": "2026-02-03T10:30:00", "exit_time": "2026-02-03T15:45:00"},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2400, "exit_price": 1.2550, "lot_size": 0.15, "entry_time": "2026-02-03T09:15:00", "exit_time": "2026-02-03T11:30:00"},
    
    # Feb 4 - Losing day
    {"symbol": "USDJPY", "direction": "long", "entry_price": 150.50, "exit_price": 149.00, "lot_size": 0.25, "entry_time": "2026-02-04T13:20:00", "exit_time": "2026-02-04T16:45:00"},
    
    # Feb 5 - Winning day
    {"symbol": "AUDUSD", "direction": "long", "entry_price": 0.6450, "exit_price": 0.6520, "lot_size": 0.2, "entry_time": "2026-02-05T10:00:00", "exit_time": "2026-02-05T14:30:00"},
    
    # Feb 6 - Mixed day
    {"symbol": "USDCAD", "direction": "short", "entry_price": 1.3500, "exit_price": 1.3480, "lot_size": 0.3, "entry_time": "2026-02-06T11:00:00", "exit_time": "2026-02-06T13:15:00"},
    
    # Feb 7 - Small loss
    {"symbol": "EURUSD", "direction": "short", "entry_price": 1.0530, "exit_price": 1.0540, "lot_size": 0.1, "entry_time": "2026-02-07T09:30:00", "exit_time": "2026-02-07T10:15:00"},
    
    # Feb 10 - Big winning day (2 trades)
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0520, "exit_price": 1.0700, "lot_size": 0.4, "entry_time": "2026-02-10T13:20:00", "exit_time": "2026-02-10T16:45:00"},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2420, "exit_price": 1.2600, "lot_size": 0.35, "entry_time": "2026-02-10T10:00:00", "exit_time": "2026-02-10T12:30:00"},
    
    # Feb 11 - Overtrading day (4 trades)
    {"symbol": "EURUSD", "direction": "long", "entry_price": 1.0530, "exit_price": 1.0535, "lot_size": 0.1, "entry_time": "2026-02-11T09:30:00", "exit_time": "2026-02-11T10:15:00"},
    {"symbol": "EURUSD", "direction": "short", "entry_price": 1.0535, "exit_price": 1.0530, "lot_size": 0.1, "entry_time": "2026-02-11T10:30:00", "exit_time": "2026-02-11T11:15:00"},
    {"symbol": "GBPUSD", "direction": "short", "entry_price": 1.2480, "exit_price": 1.2475, "lot_size": 0.1, "entry_time": "2026-02-11T13:00:00", "exit_time": "2026-02-11T13:45:00"},
    {"symbol": "GBPUSD", "direction": "long", "entry_price": 1.2475, "exit_price": 1.2482, "lot_size": 0.1, "entry_time": "2026-02-11T14:00:00", "exit_time": "2026-02-11T14:45:00"},
    
    # Feb 12 - Winning day
    {"symbol": "USDJPY", "direction": "long", "entry_price": 151.00, "exit_price": 152.00, "lot_size": 0.2, "entry_time": "2026-02-12T14:00:00", "exit_time": "2026-02-12T16:30:00"},
    
    # Feb 13 - Losing day
    {"symbol": "USDCAD", "direction": "long", "entry_price": 1.3520, "exit_price": 1.3460, "lot_size": 0.3, "entry_time": "2026-02-13T11:00:00", "exit_time": "2026-02-13T14:15:00"},
    
    # Feb 14 - Small profit
    {"symbol": "EURUSD", "direction": "short", "entry_price": 1.0550, "exit_price": 1.0530, "lot_size": 0.15, "entry_time": "2026-02-14T09:30:00", "exit_time": "2026-02-14T12:00:00"}
]

print(f"Adding {len(trades)} trades...\n")

for i, trade in enumerate(trades):
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"✅ Added trade {i+1}: {trade['symbol']} on {trade['entry_time'][:10]}")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Refresh calendar
print("\n🔄 Refreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Calendar refresh: {refresh.json()}")

print("\n=== DONE ===")
