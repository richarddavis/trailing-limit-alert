#!/usr/bin/env python3
"""
BTC trailing-alert script
Adds:
  --price N           inject synthetic price (testing)
  --set-high N        manually set high watermark
  --set-low N         manually set low watermark
  --reset             clears both high & low
Env-var equivalents: SET_HIGH, SET_LOW, RESET_STATE=1
"""
import os
import json
import argparse
import pathlib
import requests

API_URL   = os.getenv("PRICE_API_URL",
          "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
ASSET, CUR = os.getenv("ASSET","bitcoin"), os.getenv("CURRENCY","usd")

DROP_PCT = float(os.getenv("DROP_THRESHOLD_PERCENT") or 5)
RISE_PCT = float(os.getenv("RISE_THRESHOLD_PERCENT") or 5)
STATE = pathlib.Path(".btc_state.json")

PUSHOVER_APP = os.getenv("PUSHOVER_APP_TOKEN")
PUSHOVER_USER= os.getenv("PUSHOVER_USER_KEY")

# ---------- helpers ----------
def fetch_price() -> float:
    r = requests.get(API_URL, timeout=10)
    r.raise_for_status()
    return r.json()[ASSET][CUR]

def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"high": 0, "low": 0}

def save_state(s: dict):
    STATE.write_text(json.dumps(s, separators=(",",":")))

def alert(msg: str):
    if not (PUSHOVER_APP and PUSHOVER_USER):
        print("⚠ not configured, alert suppressed:", msg)
        return
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token":PUSHOVER_APP, "user":PUSHOVER_USER,
        "title":"BTC Trailing Alert","message":msg})
    print("Pushover", r.status_code, r.text[:120])

# ---------- main ----------
def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--price",    type=float)
    ap.add_argument("--set-high", type=float)
    ap.add_argument("--set-low",  type=float)
    ap.add_argument("--reset",    action="store_true")
    args = ap.parse_args(argv)

    st = load_state()
    high, low = st["high"], st["low"]

    # Handle manual overrides / resets
    reset_flag = args.reset or (os.getenv("RESET_STATE") or "").lower() in ("1", "true", "yes")
    if reset_flag:
        high = low = 0
    if args.set_high or os.getenv("SET_HIGH"):
        high = float(args.set_high or os.getenv("SET_HIGH"))
    if args.set_low  or os.getenv("SET_LOW"):
        low  = float(args.set_low  or os.getenv("SET_LOW"))

    price = args.price if args.price is not None else fetch_price()

    # Update extrema
    high = max(high, price) if not args.set_high else high
    low  = price if low==0 else min(low, price)   if not args.set_low  else low

    # ▼ drop from high
    if DROP_PCT>0 and high and price <= high*(1-DROP_PCT/100):
        alert(f"▼ BTC −{DROP_PCT}%: {high:,.0f}→{price:,.0f} USD")
        high = price  # reset after alert
    # ▲ rise from low
    if RISE_PCT>0 and low  and price >= low*(1+RISE_PCT/100):
        alert(f"▲ BTC +{RISE_PCT}%: {low:,.0f}→{price:,.0f} USD")
        low = price   # reset

    save_state({"high":high,"low":low})
    print(f"${price:,.0f} | high {high:,.0f} | low {low:,.0f}")

if __name__ == "__main__":
    main() 