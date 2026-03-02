#!/usr/bin/env python3
"""
Generate minimal trades for testing
"""

import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/trades/"

def main():
    print("Adding 5 test trades...")
    
    base_date = datetime(2026, 1, 15)
    
    for i in range(5):
        trade = {
            "symbol": "EURUSD",
            "direction": "long",
            "entry_price": 1.05 + (i * 0.001),
            "exit_price": 1.06 + (i * 0.001),
            "lot_size": 0.1,
            "entry_time": (base_date + timedelta(days=i)).isoformat(),
            "exit_time": (base_date + timedelta(days=i, hours=3)).isoformat()
        }
        
        print(f"Sending trade {i+1}: {trade}")
        try:
            response = requests.post(API_URL, json=trade)
            if response.status_code == 200:
                print(f"  ✅ Success: {response.json()}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                print(f"     Response: {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    main()
