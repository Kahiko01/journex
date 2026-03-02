import requests
import json

print("=== FIXING TRADES ===\n")

# First, get all trades
response = requests.get('http://localhost:8000/api/v1/trades/')
trades = response.json()
print(f"Found {len(trades)} trades\n")

# February dates for each trade (matching the ones we added)
feb_dates = [
    '2026-02-03', '2026-02-04', '2026-02-05', '2026-02-06', '2026-02-07',
    '2026-02-10', '2026-02-10', '2026-02-11', '2026-02-11', '2026-02-11',
    '2026-02-12', '2026-02-13', '2026-02-14'
]

print("Updating trades with exit times...\n")

for i, trade in enumerate(trades):
    if i < len(feb_dates):
        date_str = feb_dates[i]
        
        # Create update data
        update_data = {
            "exit_price": trade.get('exit_price') or (
                1.065 if i in [0,5,6] else  # Winning trades
                1.245 if i == 1 else         # Losing trade
                152.0 if i == 2 else         # Winning
                0.652 if i == 3 else         # Winning
                1.351 if i == 4 else         # Small loss
                1.0535 if i in [7,8] else    # Scalping
                1.2475 if i == 9 else        # Scalping
                152.0 if i == 10 else        # Winning
                1.346 if i == 11 else        # Big loss
                1.053                          # Small profit
            ),
            "exit_time": f"{date_str}T{15 + i}:{30 + i}:00"
        }
        
        # Update the trade (you'll need to add a PUT endpoint)
        print(f"Would update trade {trade['id']} on {date_str}")
        
        # For now, we'll delete and recreate
        
        # Delete old trade
        delete_response = requests.delete(f'http://localhost:8000/api/v1/trades/{trade["id"]}')
        if delete_response.status_code == 200:
            print(f"  ✅ Deleted trade {trade['id']}")
            
            # Create new trade with proper data
            new_trade = {
                "symbol": trade['symbol'],
                "direction": trade['direction'],
                "entry_price": trade['entry_price'],
                "exit_price": update_data['exit_price'],
                "lot_size": trade['lot_size'],
                "entry_time": f"{date_str}T10:00:00",
                "exit_time": update_data['exit_time']
            }
            
            create_response = requests.post('http://localhost:8000/api/v1/trades/', json=new_trade)
            if create_response.status_code == 200:
                print(f"  ✅ Recreated trade {trade['symbol']} on {date_str}")
            else:
                print(f"  ❌ Failed to recreate: {create_response.status_code}")

print("\n✅ Fix complete! Refreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Calendar refresh: {refresh.json()}")
