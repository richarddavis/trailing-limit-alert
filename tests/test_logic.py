"""
Deterministic tests – no HTTP, no Pushover.
Run: pytest -q
"""
import json
import pathlib
import os
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import trailing_alerts as ta  # noqa: E402

def run_once(tmp_path, price, start_state, **env):
    """helper to invoke main() with injected price & temp state."""
    (tmp_path / ".btc_state.json").write_text(json.dumps(start_state))
    original_cwd = os.getcwd()
    original_env = {}
    
    # Save and set environment variables
    for k, v in env.items():
        original_env[k] = os.environ.get(k)
        os.environ[k] = str(v)
    
    try:
        os.chdir(tmp_path)
        ta.main(["--price", str(price)])
        state = json.loads((tmp_path / ".btc_state.json").read_text())
        return state
    finally:
        # Restore original state
        os.chdir(original_cwd)
        for k, v in original_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def test_drop_alert(tmp_path, monkeypatch):
    # To disable notifications during testing, set DISABLE_NOTIFICATIONS=1
    if os.environ.get("DISABLE_NOTIFICATIONS") == "1":
        monkeypatch.setenv("PUSHOVER_APP_TOKEN", "")  # disable network
        monkeypatch.setenv("PUSHOVER_USER_KEY",  "")
        monkeypatch.setattr(ta, "alert", lambda *a, **k: None)

    state = run_once(tmp_path, 60_000, {"high": 60_000, "low": 60_000},
                     DROP_THRESHOLD_PERCENT=10, RISE_THRESHOLD_PERCENT=10)
    # 10% drop triggers, high reset
    state = run_once(tmp_path, 53_900, state,
                     DROP_THRESHOLD_PERCENT=10, RISE_THRESHOLD_PERCENT=10)
    assert state["high"] == 53_900
    assert state["low"] == 53_900

def test_rise_alert(tmp_path, monkeypatch):
    # To disable notifications during testing, set DISABLE_NOTIFICATIONS=1
    if os.environ.get("DISABLE_NOTIFICATIONS") == "1":
        monkeypatch.setenv("PUSHOVER_APP_TOKEN", "")
        monkeypatch.setenv("PUSHOVER_USER_KEY",  "")
        monkeypatch.setattr(ta, "alert", lambda *a, **k: None)

    state = run_once(tmp_path, 50_000, {"high": 50_000, "low": 50_000},
                     DROP_THRESHOLD_PERCENT=10, RISE_THRESHOLD_PERCENT=10)
    # 10% rise triggers, low reset
    state = run_once(tmp_path, 55_100, state,
                     DROP_THRESHOLD_PERCENT=10, RISE_THRESHOLD_PERCENT=10)
    assert state["low"] == 55_100
    assert state["high"] == 55_100 