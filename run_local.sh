#!/bin/bash
# Convenience script for local testing
# Usage: ./run_local.sh [script arguments]

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Copy .env.example to .env and add your credentials:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

echo "📁 Loading environment from .env..."
set -a  # automatically export all variables
source .env
set +a  # turn off automatic export

echo "🐍 Activating virtual environment..."
source .venv/bin/activate

echo "🚀 Running trailing_alerts.py $@"
echo "💡 Tip: To test without notifications, set DISABLE_NOTIFICATIONS=1"
python trailing_alerts.py "$@" 