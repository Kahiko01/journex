#!/usr/bin/env python3
"""
Generate 2 months of realistic trading data for a $1M account
Fixed version for PostgreSQL
"""

import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/trades/"
ACCOUNT_BALANCE = 1_000_000

SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
STRATEGIES = ['Trend Following', 'Breakout', 'Swing Trading', 'Scalping', 'Mean Reversion']
EMOTIONS = ['Calm', 'Confident', 'Neutral', 'Anxious', 'Greedy', 'Fearful']

def generate_trade(date):
    """Generate a single trade with proper fields"""
    symbol = random.choice(SYMBOLS)
    direction = random.choice(['long', 'short'])
    strategy = random.choice(STRATEGIES)
    emotion = random.choice(EMOTIONS)
    
    # Generate realistic prices
    if symbol == 'USDJPY':
        entry = round(random.uniform(148.0, 152.0), 2)
        exit = entry + random.uniform(-2.0, 2.0)
    else:
        entry = round(random.uniform(1.04, 1.08), 5)
        exit = entry + random.uniform(-0.003, 0.003)
    
    # Random lot size between 0.1 and 2.0
    lot_size = round(random.uniform(0.1, 2.0), 2)
    
    # Random stop loss (20-50 pips away)
    if symbol == 'USDJPY':
        stop_loss_pips = random.randint(20, 50) * 0.01
    else:
        stop_loss_pips = random.randint(20, 50) * 0.0001
    
    if direction == 'long':
        stop_loss = entry - stop_loss_pips
    else:
        stop_loss = entry + stop_loss_pips
    
    # Random time during trading hours
    hour = random.randint(8, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    entry_time = date.replace(hour=hour, minute=minute, second=second)
    exit_time = entry_time + timedelta(hours=random.randint(1, 4))
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry,
        "exit_price": exit,
        "stop_loss": stop_loss,
        "lot_size": lot_size,
        "strategy": strategy,
        "emotion": emotion,
        "rating": random.randint(1, 5),
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat()
    }

def main():
    print("=" * 60)
    print("GENERATING 2 MONTHS OF TRADING DATA FOR $1M ACCOUNT")
    print("=" * 60)
    
    # Generate dates for Jan-Feb 2026 (weekdays only)
    dates = []
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 2, 28)
    current = start_date
    
    while current <= end_date:
        if current.weekday() < 5:  # Monday=0, Friday=4
            dates.append(current)
        current += timedelta(days=1)
    
    print(f"\nGenerating trades for {len(dates)} trading days...")
    
    all_trades = []
    
    for i, date in enumerate(dates):
        # 0-4 trades per day
        num_trades = random.randint(0, 4)
        
        for _ in range(num_trades):
            trade = generate_trade(date)
            all_trades.append(trade)
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {len(all_trades)} trades so far...")
    
    print(f"\nTotal trades generated: {len(all_trades)}")
    
    # Upload to API
    print("\n" + "=" * 60)
    print("UPLOADING TRADES TO API")
    print("=" * 60)
    
    # First, check if API is available
    try:
        health = requests.get("http://localhost:8000/")
        if health.status_code != 200:
            print("❌ API is not available. Make sure the backend is running.")
            return
    except:
        print("❌ Cannot connect to API. Make sure the backend is running on port 8000.")
        return
    
    success_count = 0
    for i, trade in enumerate(all_trades):
        try:
            response = requests.post(API_URL, json=trade)
            if response.status_code == 200:
                success_count += 1
            else:
                print(f"  Failed to upload trade {i+1}: {response.status_code} - {response.text}")
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i+1}/{len(all_trades)}")
                
        except Exception as e:
            print(f"  Error uploading trade {i+1}: {e}")
    
    print(f"\n✅ Successfully uploaded {success_count} out of {len(all_trades)} trades")

if __name__ == "__main__":
    main()
