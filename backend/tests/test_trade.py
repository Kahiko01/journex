import requests
import json

print("=== TESTING TRADE CREATION ===\n")

# Try different trade formats to see what works

# Format 1: Minimal trade
trade1 = {
    "symbol": "EURUSD",
    "direction": "long",
    "entry_price": 1.05,
    "lot_size": 0.1
}

# Format 2: Trade with exit
trade2 = {
    "symbol": "EURUSD",
    "direction": "long",
    "entry_price": 1.05,
    "exit_price": 1.06,
    "lot_size": 0.1
}

# Format 3: Trade with dates
trade3 = {
    "symbol": "EURUSD",
    "direction": "long",
    "entry_price": 1.05,
    "exit_price": 1.06,
    "lot_size": 0.1,
    "entry_time": "2026-02-03T10:00:00",
    "exit_time": "2026-02-03T15:00:00"
}

trades_to_test = [trade1, trade2, trade3]

for i, trade in enumerate(trades_to_test):
    print(f"\n--- Testing Trade Format {i+1} ---")
    print(json.dumps(trade, indent=2))
    
    try:
        response = requests.post('http://localhost:8000/api/v1/trades/', json=trade)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print("Response:", json.dumps(response.json(), indent=2))
            break
        else:
            print("❌ Failed")
            print("Error:", response.text)
    except Exception as e:
        print(f"Exception: {e}")

print("\n=== TEST COMPLETE ===")
