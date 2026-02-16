import requests
import json

# Use the same headers as curl
headers = {
    'User-Agent': 'curl/8.9.1',
    'Accept': '*/*'
}

print("=== FETCHING TRADES WITH CURL-LIKE HEADERS ===\n")

try:
    # Get trades
    response = requests.get('http://localhost:8000/api/v1/trades/', headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        trades = response.json()
        print(f"\nFound {len(trades)} trades")
        
        if len(trades) > 0:
            print("\nFirst trade:")
            print(json.dumps(trades[0], indent=2))
        else:
            print("No trades in response")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n=== DONE ===")
