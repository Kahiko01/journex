import requests
import json

print("=== FORCE CALENDAR UPDATE ===\n")

# First, let's get all trades
trades_response = requests.get('http://localhost:8000/api/v1/trades/')
trades = trades_response.json()
print(f"Total trades: {len(trades)}")

# Count trades with exit_time
with_exit = 0
for trade in trades:
    if trade.get('exit_time'):
        with_exit += 1
print(f"Trades with exit_time: {with_exit}")

# Now let's manually call the month endpoint to force aggregation
print("\n📅 Fetching February calendar to force aggregation...")
cal_response = requests.get('http://localhost:8000/api/v1/calendar/month/2026/2?user_id=1')
if cal_response.status_code == 200:
    cal_data = cal_response.json()
    print("✅ Calendar endpoint responded")
    
    # Count days with data
    days_with_data = 0
    for week in cal_data.get('heatmap', []):
        for day in week:
            if not day.get('empty') and day.get('has_data'):
                days_with_data += 1
                print(f"  📅 {day.get('date')}: {day.get('trades')} trades")
    print(f"\nTotal days with trades: {days_with_data}")
else:
    print(f"❌ Calendar endpoint error: {cal_response.status_code}")
    print(cal_response.text)

print("\n=== DONE ===")
