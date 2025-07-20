#!/usr/bin/env python3
"""
Quick status checker for BTC trailing alert bot
"""
import json
import pathlib
import requests

def fetch_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["bitcoin"]["usd"]

def load_state():
    state_file = pathlib.Path(".btc_state.json")
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {"high": 0, "low": 0}

def main():
    try:
        price = fetch_price()
        state = load_state()
        
        print(f"🪙 Current BTC Price: ${price:,.2f}")
        print(f"📈 Session High:      ${state['high']:,.2f}")
        print(f"📉 Session Low:       ${state['low']:,.2f}")
        
        if state['high'] > 0:
            drop_pct = ((state['high'] - price) / state['high']) * 100
            print(f"📊 Drop from High:    {drop_pct:.1f}%")
        
        if state['low'] > 0:
            rise_pct = ((price - state['low']) / state['low']) * 100
            print(f"📊 Rise from Low:     {rise_pct:.1f}%")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 