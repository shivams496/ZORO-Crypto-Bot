"""
zoro/live_runner.py — Runs the ZORO trading loop + FastAPI server as
background threads inside the Streamlit process.

Why this exists
----------------
Hugging Face Spaces only run ONE process. The original design (trader.py +
FastAPI + Postgres, wired together via docker-compose) needs three. This
module collapses the trading loop and the API server into the same process
as the dashboard, and uses SQLite instead of Postgres, so the whole system
runs live on a single free Space.

Call start_live_system() once — the caller (dashboard.py) wraps it in
st.cache_resource so it only ever starts one set of threads per server
process, no matter how many browser tabs/sessions hit the Space.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime

import pytz

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
logging.getLogger("tensorflow").setLevel(logging.ERROR)

log = logging.getLogger("zoro.live_runner")

_STATE_LOCK = threading.Lock()
_STARTED = False

# In-memory shared state, read by the dashboard directly (and also mirrored
# into api.py's globals so the existing /signal, /status endpoints keep working)
latest_signals: dict = {}
open_positions: dict = {}
_last_alert_key: dict = {}   # symbol -> last (direction, actionable) we alerted on


def _run_api_server():
    """Serve the existing FastAPI app on :8000 inside this process."""
    import uvicorn
    import api as _api

    # Point api.py's module-level dicts at the SAME objects this module uses,
    # so /signal and /status reflect live data without any network hop.
    _api._latest_signals = latest_signals
    _api._open_positions = open_positions

    config = uvicorn.Config(_api.app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def _run_scan_loop():
    """Equivalent of trader.py's run_loop(), adapted to run as a thread."""
    from zoro.alerts import send_email, send_telegram, signal_message
    from zoro.config import config
    from zoro.data import fetch_crypto_data
    from zoro.database import init_db, insert_signal, insert_trade
    from zoro.signals import run_signal_engine

    india_tz = pytz.timezone(config.TIMEZONE)
    init_db()
    log.info("[LIVE] Scan loop starting — coins=%s interval=%ss",
              list(config.COINS), config.CHECK_INTERVAL_SEC)

    while True:
        now = datetime.now(india_tz)
        for symbol in config.COINS:
            try:
                df = fetch_crypto_data(symbol)
                if df is None:
                    continue
                result = run_signal_engine(symbol, df)
                if result is None:
                    continue

                row = {
                    "timestamp": now, "symbol": result.symbol,
                    "direction": result.direction, "confidence": result.confidence,
                    "rsi": result.rsi, "lstm_prob": result.lstm_prob,
                    "rl_signal": result.rl_signal, "price": result.price,
                    "actionable": str(result.actionable).lower(),
                }
                insert_signal(row)
                latest_signals[symbol] = {**row, "timestamp": now.isoformat()}

                # ── Fire alert only on a NEW actionable signal (no spam) ──
                alert_key = (result.direction, result.actionable)
                if result.actionable and _last_alert_key.get(symbol) != alert_key:
                    _last_alert_key[symbol] = alert_key
                    msg = signal_message(
                        symbol, result.direction, result.price,
                        result.confidence, result.gates, result.stop_loss,
                    )
                    send_telegram(msg)
                    send_email(f"ZORO {result.direction} — {symbol}",
                               msg.replace("<b>", "").replace("</b>", ""))
                    insert_trade({
                        "timestamp": now, "symbol": result.symbol, "action": result.direction,
                        "price": result.price, "qty": config.POSITION_SIZE_USD / result.price,
                        "position_value": result.price, "stop_loss": result.stop_loss,
                        "take_profit": None, "pnl": None, "rsi": result.rsi,
                        "confidence": result.confidence, "direction": result.direction,
                        "rl_signal": result.rl_signal, "lstm_prob": result.lstm_prob,
                        "coin": symbol.replace("-USD", ""),
                    })
                elif not result.actionable:
                    _last_alert_key.pop(symbol, None)

            except Exception as e:
                log.warning("[LIVE] scan failed for %s: %s", symbol, e)

        time.sleep(config.CHECK_INTERVAL_SEC)


def start_live_system():
    """Idempotent: only ever starts the threads once per process."""
    global _STARTED
    with _STATE_LOCK:
        if _STARTED:
            return
        _STARTED = True
        threading.Thread(target=_run_api_server, daemon=True, name="zoro-api").start()
        threading.Thread(target=_run_scan_loop, daemon=True, name="zoro-scanner").start()
        log.info("[LIVE] ZORO background system started (API :8000 + scanner)")
