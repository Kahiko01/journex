import requests
import json

print("=== ADDING TRADES ===\n")

# Define trades directly in Python
trades = [
    {
        "symbol": "EURUSD",
        "direction": "long",
        "entry_price": 1.05,
        "lot_size": 0.1
    }
]

for i, trade in enumerate(trades):
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        if response.status_code == 200:
            print(f"✅ Added trade {i+1}: {trade['symbol']}")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n✅ Done!")
