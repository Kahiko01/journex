import requests
import json

print("=== ADDING TRADES FROM JSON ===\n")

# Load trades from JSON file
with open('trades.json', 'r') as f:
    trades = json.load(f)

print(f"Loaded {len(trades)} trades from file\n")

# Add each trade
for i, trade in enumerate(trades):
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"✅ Added trade {i+1}: {trade['symbol']} on {trade['entry_time'][:10]}")
        else:
            print(f"❌ Failed to add trade {i+1}: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error adding trade {i+1}: {e}")

# Refresh calendar
print("\n🔄 Refreshing calendar...")
refresh = requests.post('http://localhost:8000/api/v1/calendar/refresh?user_id=1')
print(f"Calendar refresh result: {refresh.json()}")

print("\n=== DONE ===")
