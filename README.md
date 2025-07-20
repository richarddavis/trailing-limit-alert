# BTC Trailing Alert Bot

Serverless bot that tracks Bitcoin price, remembers session **high** / **low**, and
pushes notifications when:

* price drops `DROP_THRESHOLD_PERCENT` % from the high (`▼` alert)
* price rises  `RISE_THRESHOLD_PERCENT` % from the low  (`▲` alert)

Runs every 5 min on GitHub Actions – no server, no cost.

## Quick start

```bash
git clone https://github.com/yourname/btc-trailing-alert.git
cd btc-trailing-alert
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PUSHOVER_APP_TOKEN=xxx  PUSHOVER_USER_KEY=yyy
python trailing_alerts.py --reset   # initialise state
```

## Setup

### 1. Get Pushover credentials

1. **Sign up** at [pushover.net](https://pushover.net)
2. **Install the Pushover app** on your mobile device
3. **Get your User Key**: Visible on your [Pushover dashboard](https://pushover.net) when logged in
4. **Create an application**: 
   - Go to [Create an Application/API Token](https://pushover.net/apps/build)
   - Give it a name like "BTC Alerts"
   - Copy the **App Token** (API Token) 

**Note**: You need both the User Key AND an App Token - there's no way around creating an app in Pushover's system.

**Device Names**: By default, notifications are sent to ALL devices registered to your User Key. If you want to send to specific devices only, you can modify the script to include a device parameter, but for most users, the default behavior is perfect.

### 2. Configure GitHub repository

Fork this repository and set these **Repository Secrets** (Settings → Secrets and variables → Actions):

- `PUSHOVER_APP_TOKEN`: Your app token from step 1
- `PUSHOVER_USER_KEY`: Your user key from step 1
- `DROP_THRESHOLD_PERCENT`: Percentage drop to trigger alerts (e.g., `5`)
- `RISE_THRESHOLD_PERCENT`: Percentage rise to trigger alerts (e.g., `5`)

### 3. Enable GitHub Actions

The bot will automatically start running every 5 minutes via GitHub Actions.

## Usage

### Manual triggers

You can manually trigger the alert via GitHub Actions:

1. Go to Actions → "BTC Trailing Alerts"
2. Click "Run workflow"
3. Optionally set override values or reset state

### Command line

Local testing and management:

```bash
# Normal operation (fetches live price)
python trailing_alerts.py

# Testing with synthetic price
python trailing_alerts.py --price 50000

# Manual state management
python trailing_alerts.py --set-high 60000
python trailing_alerts.py --set-low 45000
python trailing_alerts.py --reset

# View current state
cat .btc_state.json
```

### Environment variables

All CLI options have environment equivalents:

- `DROP_THRESHOLD_PERCENT`: Drop percentage to trigger alerts
- `RISE_THRESHOLD_PERCENT`: Rise percentage to trigger alerts  
- `SET_HIGH`: Override high watermark
- `SET_LOW`: Override low watermark
- `RESET_STATE=1`: Clear both high and low
- `PUSHOVER_APP_TOKEN`: Pushover app token
- `PUSHOVER_USER_KEY`: Pushover user key
- `PRICE_API_URL`: Custom price API (default: CoinGecko)
- `ASSET`: Asset to track (default: bitcoin)
- `CURRENCY`: Currency for pricing (default: usd)

## How it works

The bot maintains a simple state file (`.btc_state.json`) with:
- `high`: Highest price seen in current session
- `low`: Lowest price seen in current session

**Drop alerts (`▼`)**: When price falls `DROP_THRESHOLD_PERCENT`% from the high, send alert and reset high to current price.

**Rise alerts (`▲`)**: When price rises `RISE_THRESHOLD_PERCENT`% from the low, send alert and reset low to current price.

This creates a "trailing stop" behavior that adapts to market conditions.

## Development

### Testing with Real Notifications

**By default, tests WILL send real notifications** if you have Pushover credentials configured. This lets you test both the logic AND the notification delivery.

- ✅ **Test with notifications**: `pytest -q` (tests your complete setup)
- ⚠️ **Test without notifications**: `DISABLE_NOTIFICATIONS=1 pytest -q` (logic only)

**Note**: The tests simulate a 10% price drop and rise, so you'll receive 2 test notifications if Pushover is configured.

### Run tests

```bash
# Run tests (WILL send real notifications if .env configured)
pytest -q

# Run tests WITHOUT sending notifications
DISABLE_NOTIFICATIONS=1 pytest -q

# Or add DISABLE_NOTIFICATIONS=1 to your .env file to disable permanently
```

### Project structure

```
btc-trailing-alert/
├── .github/workflows/
│   ├── alerts.yml          ← production workflow (5-min schedule)
│   └── tests.yml           ← CI workflow (runs on push/PR)
├── tests/
│   └── test_logic.py       ← deterministic unit tests
├── trailing_alerts.py      ← main script
├── requirements.txt        ← pinned dependencies
├── README.md               ← this file
└── .gitignore
```

### State persistence

The `.btc_state.json` file is automatically committed back to the repository by the GitHub Action, ensuring state persists between runs.

## Troubleshooting

### No alerts received

1. Check Repository Secrets are set correctly
2. Verify Pushover app token and user key
3. Check Actions logs for errors
4. Ensure thresholds are reasonable (try 1-2% for testing)

### Test alerts

```bash
# Send a test alert with current price
python trailing_alerts.py --reset
python trailing_alerts.py --set-high 1  # artificially low high
python trailing_alerts.py               # should trigger drop alert
```

### State issues

If the bot gets stuck or state becomes corrupted:

```bash
# Reset via GitHub Actions
# Go to Actions → "BTC Trailing Alerts" → "Run workflow" → check "Reset highs/lows?"

# Or reset locally
python trailing_alerts.py --reset
```

## License

MIT - feel free to modify and redistribute. 