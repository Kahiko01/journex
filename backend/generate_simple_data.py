#!/usr/bin/env python3
"""
Generate simple trading data with only required fields
"""

import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/trades/"
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY']

def generate_trade(date):
    """Generate a trade with only essential fields"""
    symbol = random.choice(SYMBOLS)
    direction = random.choice(['long', 'short'])
    
    # Simple price generation
    if symbol == 'USDJPY':
        entry = round(random.uniform(148.0, 152.0), 2)
        exit = entry + random.uniform(-1.0, 1.0)
    else:
        entry = round(random.uniform(1.04, 1.08), 5)
        exit = entry + random.uniform(-0.001, 0.001)
    
    lot_size = round(random.uniform(0.1, 1.0), 2)
    
    # Simple time
    hour = random.randint(8, 16)
    minute = random.randint(0, 59)
    
    entry_time = date.replace(hour=hour, minute=minute)
    exit_time = entry_time + timedelta(hours=random.randint(1, 3))
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry,
        "exit_price": exit,
        "lot_size": lot_size,
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat()
    }

def main():
    print("Generating simple trades...")
    
    # Generate just 10 trades for testing
    dates = []
    start_date = datetime(2026, 1, 1)
    for i in range(10):
        dates.append(start_date + timedelta(days=i*2))
    
    trades = []
    for date in dates:
        trades.append(generate_trade(date))
    
    print(f"Generated {len(trades)} trades")
    
    # Upload one by one
    success = 0
    for i, trade in enumerate(trades):
        try:
            response = requests.post(API_URL, json=trade)
            if response.status_code == 200:
                success += 1
                print(f"✓ Trade {i+1} successful")
            else:
                print(f"✗ Trade {i+1} failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\nSuccessfully uploaded {success}/{len(trades)} trades")

if __name__ == "__main__":
    main()
