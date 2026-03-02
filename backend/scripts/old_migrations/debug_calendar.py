import requests
import json
from datetime import datetime

print("=== DEBUGGING CALENDAR ISSUE ===\n")

# Check all trades
print("1. Fetching all trades...")
trades_response = requests.get('http://localhost:8000/api/v1/trades/')
trades = trades_response.json()
print(f"Found {len(trades)} trades\n")

if len(trades) == 0:
    print("❌ No trades found! Check if trades were added.")
    exit()

# Check first trade details
print("2. First trade details:")
first_trade = trades[0]
print(json.dumps(first_trade, indent=2))

# Check date formats
print("\n3. Checking date formats:")
for i, trade in enumerate(trades[:3]):  # Check first 3 trades
    print(f"\nTrade {i+1}:")
    print(f"  entry_time: {trade.get('entry_time')}")
    print(f"  exit_time: {trade.get('exit_time')}")
    if trade.get('exit_time'):
        try:
            # Try to parse the date
            dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
            print(f"  ✅ Parsable: {dt.date()}")
        except Exception as e:
            print(f"  ❌ Date parse error: {e}")

# Check calendar endpoint directly
print("\n4. Fetching February calendar...")
cal_response = requests.get('http://localhost:8000/api/v1/calendar/month/2026/2?user_id=1')
cal_data = cal_response.json()

# Count days with trades
days_with_trades = 0
for week in cal_data.get('heatmap', []):
    for day in week:
        if not day.get('empty') and day.get('has_data'):
            days_with_trades += 1
            print(f"  📅 {day.get('date')}: {day.get('trades')} trades, P/L: {day.get('pl')}")

print(f"\n5. Calendar shows {days_with_trades} days with trades")

# Manual refresh
print("\n6. Forcing calendar refresh...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Refresh result: {refresh.json()}")

print("\n=== DEBUG COMPLETE ===")
