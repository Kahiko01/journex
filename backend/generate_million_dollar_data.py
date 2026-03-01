#!/usr/bin/env python3
"""
Generate 2 months of realistic trading data for a $1M account
"""

import requests
import json
import random
from datetime import datetime, timedelta
import math

# Configuration
API_URL = "http://localhost:8000/api/v1/trades/"
USER_ID = 1
ACCOUNT_BALANCE = 1_000_000  # $1M

# Trading pairs
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
    
# Strategies
STRATEGIES = [
    'Trend Following', 'Breakout', 'Swing Trading', 'Scalping', 
    'Mean Reversion', 'News Trading', 'Fibonacci Retracement',
    'Support/Resistance', 'Moving Average Crossover', 'RSI Strategy'
]

# Emotions
EMOTIONS = ['Calm', 'Confident', 'Neutral', 'Anxious', 'Greedy', 'Fearful']

# Generate dates for January and February 2026
def generate_dates():
    dates = []
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 2, 28)
    current = start_date
    while current <= end_date:
        # Skip weekends (Saturday=5, Sunday=6)
        if current.weekday() < 5:  # Monday=0, Friday=4
            dates.append(current)
        current += timedelta(days=1)
    return dates

# Generate realistic price data based on symbol
def get_price_data(symbol, direction):
    """Generate realistic entry/exit prices"""
    base_prices = {
        'EURUSD': 1.05,
        'GBPUSD': 1.25,
        'USDJPY': 150.0,
        'AUDUSD': 0.65,
        'USDCAD': 1.35,
        'NZDUSD': 0.61,
        'USDCHF': 0.89
    }
    
    base = base_prices.get(symbol, 1.0)
    
    # For forex, price movements are in pips (0.0001 for most, 0.01 for JPY pairs)
    if symbol == 'USDJPY':
        pip_size = 0.01
        move = random.randint(10, 150) * pip_size
    else:
        pip_size = 0.0001
        move = random.randint(5, 200) * pip_size
    
    if direction == 'long':
        entry = base + random.uniform(-0.001, 0.001)
        exit = entry + move
    else:
        entry = base + random.uniform(-0.001, 0.001)
        exit = entry - move
    
    return round(entry, 5), round(exit, 5)

# Calculate lot size based on risk (0.5% to 2% of account)
def calculate_lot_size(entry_price, stop_loss_pips, risk_percent):
    """Calculate lot size for forex (standard lot = 100,000 units)"""
    pip_value_per_lot = 10  # $10 per pip for standard lot on major pairs
    risk_amount = ACCOUNT_BALANCE * (risk_percent / 100)
    pips_at_risk = stop_loss_pips
    lot_size = risk_amount / (pips_at_risk * pip_value_per_lot)
    return round(lot_size, 2)

# Generate a single trade
def generate_trade(date, prev_equity):
    symbol = random.choice(SYMBOLS)
    direction = random.choice(['long', 'short'])
    strategy = random.choice(STRATEGIES)
    emotion = random.choice(EMOTIONS)
    
    # Risk between 0.3% and 1.5% of account
    risk_percent = random.uniform(0.3, 1.5)
    
    # Generate prices
    entry, exit = get_price_data(symbol, direction)
    
    # Determine stop loss in pips (15-50 pips)
    if symbol == 'USDJPY':
        stop_loss_pips = random.randint(15, 50)
        stop_loss = entry - (stop_loss_pips * 0.01) if direction == 'long' else entry + (stop_loss_pips * 0.01)
    else:
        stop_loss_pips = random.randint(15, 50)
        stop_loss = entry - (stop_loss_pips * 0.0001) if direction == 'long' else entry + (stop_loss_pips * 0.0001)
    
    # Calculate lot size
    lot_size = calculate_lot_size(entry, stop_loss_pips, risk_percent)
    
    # Calculate profit/loss
    if direction == 'long':
        profit_loss = (exit - entry) * lot_size * 100000
    else:
        profit_loss = (entry - exit) * lot_size * 100000
    
    # Calculate R-multiple
    if direction == 'long':
        risk_amount = (entry - stop_loss) * lot_size * 100000
    else:
        risk_amount = (stop_loss - entry) * lot_size * 100000
    
    r_multiple = profit_loss / risk_amount if risk_amount != 0 else 0
    
    # Generate random hour between 8 and 17
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    entry_time = date.replace(hour=hour, minute=minute, second=second)
    # Exit 1-4 hours later
    exit_time = entry_time + timedelta(hours=random.randint(1, 4), minutes=random.randint(0, 59))
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry,
        "exit_price": exit,
        "stop_loss": round(stop_loss, 5),
        "lot_size": lot_size,
        "strategy": strategy,
        "emotion": emotion,
        "rating": random.randint(1, 5),
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat(),
        "profit_loss": round(profit_loss, 2),
        "r_multiple": round(r_multiple, 2),
        "risk_percent": round(risk_percent, 2)
    }

# Main execution
def main():
    print("=" * 60)
    print("GENERATING 2 MONTHS OF TRADING DATA FOR $1M ACCOUNT")
    print("=" * 60)
    
    # First, clear existing trades (optional - be careful!)
    print("\n⚠️  This will add new trades to existing data.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    dates = generate_dates()
    all_trades = []
    total_pl = 0
    equity = ACCOUNT_BALANCE
    
    print(f"\nGenerating trades for {len(dates)} trading days...")
    
    for date in dates:
        # Number of trades per day (0-6, with occasional high-volume days)
        if random.random() < 0.1:  # 10% high-volume days
            num_trades = random.randint(4, 8)
        elif random.random() < 0.3:  # 30% medium-volume days
            num_trades = random.randint(2, 4)
        else:  # 60% low-volume days
            num_trades = random.randint(0, 2)
        
        day_trades = []
        day_pl = 0
        
        for _ in range(num_trades):
            trade = generate_trade(date, equity)
            day_pl += trade['profit_loss']
            all_trades.append(trade)
            day_trades.append(trade)
        
        equity += day_pl
        total_pl += day_pl
        
        # Print progress every 10 days
        if len(all_trades) % 10 == 0:
            print(f"  Generated {len(all_trades)} trades... Equity: ${equity:,.2f}")
    
    print(f"\nTotal trades generated: {len(all_trades)}")
    print(f"Final equity: ${equity:,.2f}")
    print(f"Total P/L: ${total_pl:,.2f}")
    print(f"Return: {(total_pl/ACCOUNT_BALANCE*100):.2f}%")
    
    # Upload to API
    print("\n" + "=" * 60)
    print("UPLOADING TRADES TO API")
    print("=" * 60)
    
    success_count = 0
    for i, trade in enumerate(all_trades):
        try:
            response = requests.post(API_URL, json=trade)
            if response.status_code == 200:
                success_count += 1
                if i % 20 == 0:
                    print(f"  Uploaded {i+1}/{len(all_trades)} trades...")
            else:
                print(f"  Failed to upload trade {i+1}: {response.status_code}")
        except Exception as e:
            print(f"  Error uploading trade {i+1}: {e}")
    
    print(f"\n✅ Successfully uploaded {success_count} out of {len(all_trades)} trades")
    
    # Calculate summary statistics
    winning_trades = [t for t in all_trades if t['profit_loss'] > 0]
    losing_trades = [t for t in all_trades if t['profit_loss'] < 0]
    
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Trades: {len(all_trades)}")
    print(f"Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(all_trades)*100:.1f}%)")
    print(f"Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(all_trades)*100:.1f}%)")
    
    if winning_trades:
        avg_win = sum(t['profit_loss'] for t in winning_trades) / len(winning_trades)
        print(f"Average Win: ${avg_win:,.2f}")
    if losing_trades:
        avg_loss = abs(sum(t['profit_loss'] for t in losing_trades) / len(losing_trades))
        print(f"Average Loss: ${avg_loss:,.2f}")
    
    profit_factor = abs(sum(t['profit_loss'] for t in winning_trades)) / abs(sum(t['profit_loss'] for t in losing_trades)) if losing_trades else float('inf')
    print(f"Profit Factor: {profit_factor:.2f}")
    
    avg_r = sum(t['r_multiple'] for t in all_trades) / len(all_trades)
    print(f"Average R-Multiple: {avg_r:.2f}")

if __name__ == "__main__":
    main()
