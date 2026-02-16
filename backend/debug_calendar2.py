import requests
import json
from datetime import datetime

print("=== CALENDAR DEBUG ===\n")

# Get all trades
trades_response = requests.get('http://localhost:8000/api/v1/trades/')
trades = trades_response.json()
print(f"Total trades: {len(trades)}")

if len(trades) > 0:
    print("\nFirst trade details:")
    print(json.dumps(trades[0], indent=2))
    
    # Check exit_time format
    exit_time = trades[0].get('exit_time')
    print(f"\nexit_time: {exit_time}")
    
    if exit_time:
        try:
            # Try to parse it
            dt = datetime.fromisoformat(exit_time.replace('Z', '+00:00'))
            print(f"✅ Parsable: {dt}")
            print(f"Date: {dt.date()}")
        except Exception as e:
            print(f"❌ Parse error: {e}")
else:
    print("No trades found!")

# Check all trades for exit_time
print("\n--- Checking all trades for exit_time ---")
trades_with_exit = 0
trades_without_exit = 0

for trade in trades:
    if trade.get('exit_time'):
        trades_with_exit += 1
    else:
        trades_without_exit += 1

print(f"Trades with exit_time: {trades_with_exit}")
print(f"Trades without exit_time: {trades_without_exit}")

# Try to manually aggregate February 3
print("\n--- Testing February 3, 2026 ---")
test_date = '2026-02-03'
trades_on_day = []

for trade in trades:
    if trade.get('exit_time'):
        try:
            # Try different date parsing approaches
            exit_time_str = trade['exit_time']
            
            # Approach 1: Direct ISO format
            try:
                trade_date = datetime.fromisoformat(exit_time_str.replace('Z', '+00:00')).date()
            except:
                # Approach 2: Try without timezone
                trade_date = datetime.fromisoformat(exit_time_str.split('+')[0]).date()
            
            if str(trade_date) == test_date:
                trades_on_day.append(trade)
                print(f"  Found trade: {trade['symbol']} at {exit_time_str}")
        except Exception as e:
            print(f"  Error parsing date for trade {trade['id']}: {e}")

print(f"\nTrades on {test_date}: {len(trades_on_day)}")

if len(trades_on_day) > 0:
    total_pl = 0
    for trade in trades_on_day:
        if trade['direction'] == 'long':
            pl = (trade['exit_price'] - trade['entry_price']) * trade['lot_size']
        else:
            pl = (trade['entry_price'] - trade['exit_price']) * trade['lot_size']
        total_pl += pl
        print(f"  {trade['symbol']}: ")
    print(f"Total P/L for {test_date}: ")

print("\n=== DONE ===")
