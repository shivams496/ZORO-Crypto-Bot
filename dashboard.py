"""
dashboard.py — ZORO KATANA Terminal Dashboard v2
Full production build — Zoro moss-green/dark theme · 6 tabs · live data · SHAP
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json, os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# NOTE: the live trading scanner runs as its own separate process (trader.py,
# launched by start.sh) — NOT from here. Do not re-add a live_runner boot call
# in this file; running the scanner both here AND as trader.py causes a
# duplicate scanner: double DB writes and duplicate Telegram/email alerts for
# the same signal.

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZORO — KATANA Terminal",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── KATANA Theme ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
:root {
    --red:    #C1554A;
    --red2:   #5A2620;
    --green:  #5FD98F;
    --brand:  #4C8A63;
    --brand2: #1F3D2C;
    --gold:   #ffd700;
    --bg:     #080A08;
    --bg2:    #0D120E;
    --bg3:    #14201A;
    --border: #1A241D;
    --muted:  #444;
    --dim:    #2a2a2a;
}
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: #ccc !important;
    font-family: 'Rajdhani', sans-serif !important;
}
/* Scanline overlay */
body::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    pointer-events: none; z-index: 9999;
}
/* ── HEADER ── */
.zoro-header {
    background: linear-gradient(90deg, #0A1712 0%, #0A0D0A 40%, #080A08 100%);
    border-bottom: 1px solid var(--brand2);
    padding: 0.9rem 2rem;
    margin: -1rem -1rem 0 -1rem;
    display: flex; align-items: center; gap: 1.5rem;
    position: relative; overflow: hidden;
}
.zoro-header::after {
    content: '';
    position: absolute; left: 0; bottom: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--brand) 0%, transparent 60%);
}
.zoro-logo {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem; font-weight: 900;
    color: var(--brand);
    letter-spacing: 6px;
    text-shadow: 0 0 30px rgba(76,138,99,0.6), 0 0 60px rgba(76,138,99,0.2);
    animation: flicker 6s infinite;
}
@keyframes flicker {
    0%,95%,100%{opacity:1} 96%{opacity:0.8} 97%{opacity:1} 98%{opacity:0.9}
}
.zoro-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem; color: var(--muted); letter-spacing: 3px;
}
.live-badge {
    display: flex; align-items: center; gap: 6px;
    background: #0a1a0d; border: 1px solid #1a3d1a;
    padding: 4px 12px; border-radius: 2px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem; color: var(--green);
    letter-spacing: 2px;
}
.live-dot {
    width: 7px; height: 7px; background: var(--green);
    border-radius: 50%; animation: pulse 1.5s infinite;
    box-shadow: 0 0 6px var(--green);
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
.header-right { margin-left: auto; text-align: right; }
.phase-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem; color: var(--gold);
    letter-spacing: 2px; display: block;
}
.testnet-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem; color: var(--muted);
    letter-spacing: 1px;
}
/* ── METRIC CARDS ── */
.mc {
    background: var(--bg3); border: 1px solid var(--border);
    border-top: 2px solid var(--brand2); border-radius: 3px;
    padding: 0.9rem 1.1rem; margin: 0.3rem 0;
    position: relative; overflow: hidden;
}
.mc::after {
    content: ''; position: absolute; top: 0; right: 0;
    width: 30%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--brand2));
}
.mc-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem; color: var(--muted);
    letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 0.4rem;
}
.mc-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem; font-weight: 700; color: #eee;
}
.mc-value.g { color: var(--green); text-shadow: 0 0 12px rgba(95,217,143,0.3); }
.mc-value.r { color: var(--red);   text-shadow: 0 0 12px rgba(193,85,74,0.3); }
.mc-value.y { color: var(--gold);  text-shadow: 0 0 12px rgba(255,215,0,0.2); }
.mc-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem; color: var(--muted); margin-top: 0.2rem;
}
/* ── COIN CARD ── */
.coin-card {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 3px; padding: 0.8rem;
    transition: border-color 0.2s;
}
.coin-card:hover { border-color: var(--brand2); }
.coin-name { font-family: 'Orbitron', monospace; font-size: 0.8rem; color: var(--muted); letter-spacing: 2px; }
.coin-price { font-family: 'Share Tech Mono', monospace; font-size: 1.3rem; color: #fff; margin: 0.3rem 0 0.1rem; }
.coin-pct.g { color: var(--green); font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.coin-pct.r { color: var(--red);   font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.coin-rsi { font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: var(--dim); margin-top: 4px; }
/* ── SIGNAL BADGES ── */
.sig-long  { background:#001a0d; color:var(--green); border:1px solid #5FD98F55;
             padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:0.75rem; letter-spacing:2px; }
.sig-short { background:#1a0005; color:var(--red);   border:1px solid #C1554A55;
             padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:0.75rem; letter-spacing:2px; }
.sig-flat  { background:var(--bg3); color:var(--muted); border:1px solid var(--dim);
             padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:0.75rem; letter-spacing:2px; }
/* ── SECTION TITLE ── */
.st2 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem; letter-spacing: 3px;
    color: var(--brand2); text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.35rem; margin: 1.4rem 0 0.9rem 0;
    display: flex; align-items: center; gap: 8px;
}
.st2::before { content: '//'; color: var(--brand); }
/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important; letter-spacing: 2px !important;
    color: var(--muted) !important; background: transparent !important;
    border: none !important; padding: 0.7rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--brand) !important;
    border-bottom: 2px solid var(--brand) !important;
}
/* ── PROGRESS BAR (confidence) ── */
.conf-bar-wrap { background: var(--bg2); border-radius: 2px; height: 6px; margin-top: 4px; }
.conf-bar { height: 6px; border-radius: 2px; background: linear-gradient(90deg, var(--red2), var(--red)); }
.conf-bar.high { background: linear-gradient(90deg, #1F3D2C, var(--green)); }
/* ── SHAP BAR ── */
.shap-row { display:flex; align-items:center; gap:8px; margin:6px 0; }
.shap-label { font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#888; width:130px; flex-shrink:0; }
.shap-bar-pos { height:16px; background:linear-gradient(90deg,var(--red2),var(--red)); border-radius:2px; }
.shap-bar-neg { height:16px; background:linear-gradient(90deg,#1F3D2C,var(--green)); border-radius:2px; }
.shap-pct { font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:var(--muted); width:40px; text-align:right; }
/* ── TABLE ── */
.stDataFrame { background: var(--bg3) !important; }
thead tr th { background: #0D1A12 !important; color: var(--brand) !important; font-family:'Share Tech Mono',monospace !important; font-size:0.72rem !important; }
tbody tr td { font-family:'Share Tech Mono',monospace !important; font-size:0.75rem !important; }
tbody tr:nth-child(even) td { background: var(--bg2) !important; }
/* ── INFO BOX ── */
.info-box {
    background: #0a0f0a; border: 1px solid #1a2d1a;
    border-left: 3px solid var(--green);
    padding: 0.7rem 1rem; border-radius: 3px; margin: 0.5rem 0;
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #555;
    line-height: 1.6;
}
.warn-box {
    background: #0f0a00; border: 1px solid #2d1a00;
    border-left: 3px solid var(--gold);
    padding: 0.7rem 1rem; border-radius: 3px; margin: 0.5rem 0;
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #555;
    line-height: 1.6;
}
.stale-box {
    background: #150a00; border: 1px solid #3d2200;
    border-left: 3px solid #ff9500;
    padding: 0.6rem 1rem; border-radius: 3px; margin: 0.5rem 0;
    font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #ff9500;
    line-height: 1.5;
}
.live-pill {
    display:inline-flex; align-items:center; gap:6px;
    background:#0a1a0d; border:1px solid #1a3d1a; color:var(--green);
    padding:3px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace;
    font-size:0.68rem; letter-spacing:2px;
}
.stale-pill {
    display:inline-flex; align-items:center; gap:6px;
    background:#1a1000; border:1px solid #3d2200; color:#ff9500;
    padding:3px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace;
    font-size:0.68rem; letter-spacing:2px;
}
/* ── TRADE ROW ── */
.trade-row {
    background: var(--bg3); border: 1px solid var(--border);
    border-left: 3px solid var(--brand2);
    padding: 0.6rem 1rem; margin: 0.3rem 0; border-radius: 2px;
    font-family: 'Share Tech Mono', monospace;
}
/* ── MISC ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: var(--brand2); }
div[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# REAL TRAINING RESULTS — sourced directly from retrain_report.txt / rl_train_report.txt
# Do not hand-edit these numbers; regenerate this block if the reports change.
# ══════════════════════════════════════════════════════════════════════════════
LSTM_RESULTS = {
    "train_acc": 50.0, "val_acc": 49.8, "test_acc": 53.3,
    "walk_forward": [55.3, 54.9, 49.7],   # Window 1, 2, 3
    "features": ["Close","RSI","MACD","BB_Width","ATR","SMA_20","Volume_Ratio"],
    "seq_len": 60, "horizon_h": 4,
}

RL_RESULTS = {
    "steps": 300_000,
    "coins": ["ETH-USD","BTC-USD","SOL-USD","BNB-USD","ADA-USD"],
    # Final model, single evaluation window — NOT live, NOT walk-forward
    "final_eval": {
        "ETH-USD": {"win": 88.1, "sharpe": 1.211, "trades": 67},
        "BTC-USD": {"win": 88.1, "sharpe": 1.105, "trades": 42},
        "SOL-USD": {"win": 84.4, "sharpe": 0.979, "trades": 45},
        "BNB-USD": {"win": 97.6, "sharpe": 2.465, "trades": 84},
        "ADA-USD": {"win": 68.2, "sharpe": 0.277, "trades": 66},
    },
    # Walk-forward Sharpe spread per coin — this is what actually tests consistency
    "walk_forward": {
        "ETH-USD": {"sharpes": [0.45, 0.00, 0.04], "spread": 0.45, "flag": "OK"},
        "BTC-USD": {"sharpes": [1.90, 0.00, -0.29], "spread": 2.20, "flag": "CHECK"},
        "SOL-USD": {"sharpes": [-0.11, 0.00, -0.14], "spread": 0.14, "flag": "OK"},
        "BNB-USD": {"sharpes": [-0.34, 0.00, -0.23], "spread": 0.34, "flag": "OK"},
        "ADA-USD": {"sharpes": [0.76, 0.00, 0.47], "spread": 0.76, "flag": "CHECK"},
    },
    "overall_consistent": False,  # verbatim from report: "Overall: consistent=NO"
}

def _rl_avg(field):
    vals = [v[field] for v in RL_RESULTS["final_eval"].values()]
    return sum(vals) / len(vals)

RL_WIN_AVG = _rl_avg("win")
RL_SHARPE_AVG = _rl_avg("sharpe")
RL_SHARPE_MIN = min(v["sharpe"] for v in RL_RESULTS["final_eval"].values())
RL_SHARPE_MAX = max(v["sharpe"] for v in RL_RESULTS["final_eval"].values())


# ══════════════════════════════════════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_data(symbol: str):
    try:
        import yfinance as yf
        df = yf.Ticker(symbol).history(period="14d", interval="1h")
        if df.empty:
            return None
        return df
    except Exception:
        return None

def indicators(df):
    if df is None or df.empty:
        return None
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Sig"] = df["MACD"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sig"]
    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_Up"] = bb_mid + 2*bb_std
    df["BB_Lo"] = bb_mid - 2*bb_std
    df["BB_Pos"] = (df["Close"] - df["BB_Lo"]) / (df["BB_Up"] - df["BB_Lo"] + 1e-9)
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"]  - df["Close"].shift()).abs()
    df["ATR"] = pd.concat([hl,hc,lc],axis=1).max(axis=1).rolling(14).mean()
    vol_ma = df["Volume"].rolling(20).mean()
    df["Vol_Ratio"] = df["Volume"] / (vol_ma + 1)
    return df.dropna()

def signal(symbol, df):
    if df is None or df.empty:
        return None
    r = df.iloc[-1]
    price, rsi, macd_h = float(r["Close"]), float(r["RSI"]), float(r["MACD_Hist"])
    bb_pos, sma20, sma50, atr = float(r["BB_Pos"]), float(r["SMA20"]), float(r["SMA50"]), float(r["ATR"])
    vol_ratio = float(r.get("Vol_Ratio", 1.0))
    conf = 50; direction = "FLAT"; gates = []
    if rsi < 25:   conf += 20; direction = "LONG";  gates.append(f"RSI {rsi:.1f} oversold")
    elif rsi > 75: conf += 20; direction = "SHORT"; gates.append(f"RSI {rsi:.1f} overbought")
    if price > sma20 > sma50:
        conf += 10 if direction=="LONG" else -5; gates.append("SMC bullish")
    elif price < sma20 < sma50:
        conf += 10 if direction=="SHORT" else -5; gates.append("SMC bearish")
    if macd_h > 0 and direction=="LONG":   conf+=10; gates.append("MACD ↑")
    elif macd_h < 0 and direction=="SHORT": conf+=10; gates.append("MACD ↓")
    if bb_pos <= 0.1 and direction=="LONG":   conf+=10; gates.append(f"BB {bb_pos:.2f} low")
    elif bb_pos >= 0.9 and direction=="SHORT": conf+=10; gates.append(f"BB {bb_pos:.2f} high")
    if vol_ratio > 1.5: gates.append(f"Vol {vol_ratio:.1f}x")
    lstm_prob = 0.528; gates.append(f"LSTM {lstm_prob:.1%}")
    conf = max(0, min(int(conf), 100))
    sl = price - 1.5*atr if direction=="LONG" else price + 1.5*atr if direction=="SHORT" else 0.0
    tp = price + 2.0*atr if direction=="LONG" else price - 2.0*atr if direction=="SHORT" else 0.0
    return dict(symbol=symbol, price=price, rsi=rsi, direction=direction, conf=conf,
                gates=gates, atr=atr, sl=sl, tp=tp, macd_h=macd_h, bb_pos=bb_pos,
                sma20=sma20, vol_ratio=vol_ratio)

COINS = {"ETH-USD":"ETH","BTC-USD":"BTC","SOL-USD":"SOL","BNB-USD":"BNB","ADA-USD":"ADA"}
API_BASE = "http://localhost:8000"
PLOT_BG  = "#080A08"
PLOT_BG2 = "#0D120E"
PLOT_FONT = dict(family="Share Tech Mono", color="#444", size=10)

# ── API helpers (live data from trader.py via FastAPI) ────────────────────
import requests as _req

@st.cache_data(ttl=30)
def api_signals():
    try:
        r = _req.get(f"{API_BASE}/signal", timeout=3)
        if r.ok: return r.json()
    except Exception: pass
    return {}

@st.cache_data(ttl=30)
def api_trades(limit=50):
    """Returns (trades, is_live). is_live=False means we fell back to the
    local JSON snapshot instead of the running trader.py API."""
    try:
        r = _req.get(f"{API_BASE}/trades", params={"limit": limit}, timeout=3)
        if r.ok:
            return r.json(), True
    except Exception:
        pass
    # fallback: read local JSON snapshot (STALE — not live)
    try:
        with open("zoro_trade_log.json") as f:
            return json.load(f), False
    except Exception:
        pass
    return [], False

@st.cache_data(ttl=180)
def api_explain(symbol="BNB-USD"):
    """Calls the REAL 7-gate engine (run_signal_engine) via /explain — this is
    the only endpoint that computes a fresh signal (LSTM + FinBERT + RL + SHAP).
    /signal only reads a cache, so it is not used for live signal generation here.
    Cached 3 min since this is expensive (model load + SHAP + live FinBERT fetch)."""
    try:
        r = _req.get(f"{API_BASE}/explain", params={"symbol": symbol}, timeout=45)
        if r.ok: return r.json()
    except Exception: pass
    return None

@st.cache_data(ttl=30)
def api_status():
    try:
        r = _req.get(f"{API_BASE}/status", timeout=3)
        if r.ok: return r.json()
    except Exception: pass
    return None

@st.cache_data(ttl=30)
def api_backtest():
    """Real endpoint from api.py — NOTE: despite the name, this is LIVE paper
    trading P&L from PostgreSQL, not a historical simulation (api.py says so
    explicitly). Kept separate from the historical vectorbt bt_raw table."""
    try:
        r = _req.get(f"{API_BASE}/backtest", timeout=5)
        if r.ok: return r.json()
    except Exception: pass
    return None

def plotly_base(h=380):
    return dict(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG2,
                font=PLOT_FONT, height=h, showlegend=False,
                margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor="#111",showgrid=True,zeroline=False),
                yaxis=dict(gridcolor="#111",showgrid=True,zeroline=False))

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
now = datetime.now().strftime("%H:%M:%S  %d/%m/%Y")
st.markdown(f"""
<div class="zoro-header">
    <div>
        <div class="zoro-logo">⚔ ZORO</div>
        <div class="zoro-sub">KATANA TERMINAL &nbsp;·&nbsp; RL + LSTM + FINBERT &nbsp;·&nbsp; 5-COIN PAPER TRADER</div>
    </div>
    <div class="live-badge"><span class="live-dot"></span>LIVE</div>
    <div class="header-right">
        <span class="phase-tag">PHASE 4 COMPLETE</span>
        <span class="testnet-tag">BINANCE TESTNET &nbsp;·&nbsp; {now} IST</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Auto-refresh sidebar ──────────────────────────────────────────────────────
import time as _time
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
                color:#4C8A63;letter-spacing:2px;margin-bottom:0.5rem">
    ⚔ ZORO CONTROLS
    </div>""", unsafe_allow_html=True)
    auto_refresh = st.toggle("Auto-refresh (60s)", value=True)
    if auto_refresh:
        st.markdown("""<div style="font-family:'Share Tech Mono',monospace;
                    font-size:0.68rem;color:#444">
                    <span style="color:#5FD98F">●</span> Refreshing every 60s
                    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""<div style="font-family:'Share Tech Mono',monospace;
                font-size:0.65rem;color:#333;line-height:1.8">
                python trader.py<br>
                uvicorn api:app --port 8000<br>
                streamlit run dashboard.py
                </div>""", unsafe_allow_html=True)

# ── RSI Alert banner — shows whichever coin is in signal zone ─────────────────
all_data = {}
for _sym in COINS:
    _df = indicators(fetch_data(_sym))
    all_data[_sym] = _df

_alert_coins = []
for _sym, _ticker in COINS.items():
    _df = all_data.get(_sym)
    if _df is not None and not _df.empty:
        _rsi = float(_df["RSI"].iloc[-1])
        _price = float(_df["Close"].iloc[-1])
        if _rsi > 75:
            _alert_coins.append((_ticker, _rsi, _price, "SHORT", "#C1554A", "🔴"))
        elif _rsi < 25:
            _alert_coins.append((_ticker, _rsi, _price, "LONG", "#5FD98F", "🟢"))

if _alert_coins:
    _parts = " &nbsp;·&nbsp; ".join(
        f'<span style="color:{c}">{flag} <strong>{t}</strong> RSI {r:.1f} → {d} ZONE</span>'
        for t, r, p, d, c, flag in _alert_coins
    )
    st.markdown(f"""
    <div style="background:#0D1A12;border:1px solid #5A2620;border-left:4px solid #C1554A;
                padding:0.6rem 1rem;margin:0.5rem 0;border-radius:3px;
                font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                animation:flicker 2s infinite">
        ⚡ SIGNAL ZONE ALERT &nbsp;·&nbsp; {_parts}
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
t1,t2,t3,t4,t5,t6 = st.tabs([
    "⚡ OVERVIEW", "🎯 SIGNALS", "📈 PRICE CHART", "📊 BACKTEST", "🤖 RL AGENT", "🔬 SHAP + LOG"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    # Top stats
    st.markdown('<div class="st2">SYSTEM METRICS &nbsp; (training-time evaluation — not live)</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    cards = [
        (c1,"RL WIN RATE (AVG)",f"{RL_WIN_AVG:.1f}%","y","final eval · 5 coins · NOT live"),
        (c2,"RL SHARPE (AVG)",f"{RL_SHARPE_AVG:.2f}","y",f"range {RL_SHARPE_MIN:.2f}–{RL_SHARPE_MAX:.2f}"),
        (c3,"LSTM ACCURACY",f"{LSTM_RESULTS['test_acc']:.1f}%","y","walk-fwd 49.7–55.3%"),
        (c4,"SIGNAL THRESHOLD","70/100","","7-gate engine"),
        (c5,"WALK-FWD CONSISTENCY","NO","r","BTC & ADA flagged · see RL tab"),
        (c6,"ACTIVE COINS","5","","ETH BTC SOL BNB ADA"),
    ]
    for col,(label,val,cls,sub) in zip([c1,c2,c3,c4,c5,c6], [(x[1],x[2],x[3],x[4]) for x in cards]):
        with col:
            st.markdown(f"""
            <div class="mc">
                <div class="mc-label">{label}</div>
                <div class="mc-value {cls}">{val}</div>
                <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-box">
    ⚠️ The metrics above come from <code>rl_train_report.txt</code> / <code>retrain_report.txt</code>
    (training-time backtests on historical data). They are <strong>not live trading results</strong>
    and RL walk-forward consistency is flagged <strong>NO</strong> for BTC and ADA — see the RL AGENT tab
    for the full per-coin breakdown before citing these numbers.
    </div>""", unsafe_allow_html=True)

    # Live coin prices
    st.markdown('<div class="st2">LIVE COIN STATUS</div>', unsafe_allow_html=True)
    coin_cols = st.columns(5)
    all_data = {}
    for i,(sym,ticker) in enumerate(COINS.items()):
        df = fetch_data(sym)
        df = indicators(df)
        all_data[sym] = df
        with coin_cols[i]:
            if df is not None:
                price = df["Close"].iloc[-1]
                prev  = df["Close"].iloc[-2]
                pct   = (price-prev)/prev*100
                rsi   = df["RSI"].iloc[-1]
                atr   = df["ATR"].iloc[-1]
                cls   = "g" if pct>=0 else "r"
                sign  = "+" if pct>=0 else ""
                rsi_color = "#C1554A" if rsi>70 else "#5FD98F" if rsi<30 else "#888"
                bc = "#003d1f" if pct>=0 else "#3d0000"
                bt = "#5FD98F" if pct>=0 else "#C1554A"
                st.markdown(f"""
                <div class="coin-card" style="border-top: 2px solid {bt}">
                    <div class="coin-name">{ticker}</div>
                    <div class="coin-price">${price:,.2f}</div>
                    <div class="coin-pct {cls}">{sign}{pct:.2f}%</div>
                    <div class="coin-rsi" style="color:{rsi_color}">RSI {rsi:.1f} &nbsp;·&nbsp; ATR {atr:.2f}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="coin-card">
                    <div class="coin-name">{ticker}</div>
                    <div style="font-family:'Share Tech Mono',monospace;color:#333;font-size:0.8rem;padding:0.5rem 0">NO DATA</div>
                </div>""", unsafe_allow_html=True)

    # Architecture diagram
    st.markdown('<div class="st2">SYSTEM ARCHITECTURE</div>', unsafe_allow_html=True)
    col_arch, col_up = st.columns([2,1])
    with col_arch:
        st.code("""
┌── DATA LAYER ──────────┬── AI LAYER ─────────────┬── EXECUTION LAYER ────────────┐
│  yfinance (1H OHLC)    │  LSTM 3-layer (60h seq)  │  7-Gate Signal Engine          │
│  Binance WebSocket     │  PPO RL Agent (300k)     │  RSI 25/75 thresholds          │
│  FinBERT RSS news      │  SHAP Explainability     │  ATR stop-loss 1.5×            │
│  PostgreSQL store      │  53.3% directional acc.  │  Trailing stop 2.0×            │
└────────────────────────┴─────────────────────────┴───────────────────────────────┘
          ↓                           ↓                             ↓
  ┌──────────────────────────────────────────────────────────────────────────┐
  │   FastAPI :8000  ·  Streamlit KATANA  ·  Docker  ·  Hugging Face Spaces │
  └──────────────────────────────────────────────────────────────────────────┘
""", language="text")
    with col_up:
        st.markdown("""
        <div class="st2">UPGRADE LOG</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;line-height:2">
        <span style="color:#5FD98F">✔</span> <span style="color:#555">A</span> LSTM neural network<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">B</span> Backtesting (vectorbt)<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">C</span> Paper trading testnet<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">D</span> RL PPO agent 300k<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">E</span> KATANA dashboard<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">F</span> Short + ATR + trail<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">G</span> Telegram + 5 coins<br>
        <span style="color:#5FD98F">✔</span> <span style="color:#555">H</span> Backtest all 5 coins
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    # ── Section A: cheap local pre-screen (indicators only, no models) ────────
    st.markdown('<div class="st2">QUICK SCAN — LOCAL INDICATORS ONLY (RSI / MACD / BB)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stale-box">
    This row is a fast, free preview computed locally from price data alone — it does
    NOT include LSTM, FinBERT sentiment, or the RL agent, and its confidence score is
    a simplified approximation, not the real 7-gate engine's output. Use it to spot
    which coins are worth running the full engine on below.
    </div>""", unsafe_allow_html=True)

    for sym, ticker in COINS.items():
        _d = all_data.get(sym)
        df = _d if (_d is not None and not _d.empty) else indicators(fetch_data(sym))
        sig = signal(sym, df)

        direction = sig["direction"] if sig else "FLAT"
        conf = sig["conf"] if sig else 0
        price = sig["price"] if sig else 0
        gates = sig["gates"] if sig else []
        actionable = conf >= 70 and direction != "FLAT"

        badge = f'<span class="sig-{"long" if direction=="LONG" else "short" if direction=="SHORT" else "flat"}">{direction}</span>'
        conf_class = "high" if actionable else ""
        fire = " 🔥" if actionable else ""
        conf_color = "#5FD98F" if actionable else "#ffd700" if conf>=50 else "#333"

        with st.container():
            col_t, col_p, col_d, col_c, col_g = st.columns([0.8, 1.2, 1, 1.5, 5])
            with col_t:
                st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:0.9rem;color:#ccc;padding-top:10px'>{ticker}</div>", unsafe_allow_html=True)
            with col_p:
                st.markdown(f"<div style='font-family:Share Tech Mono,monospace;font-size:0.88rem;color:#888;padding-top:10px'>${price:,.2f}</div>", unsafe_allow_html=True)
            with col_d:
                st.markdown(f"<div style='padding-top:8px'>{badge}</div>", unsafe_allow_html=True)
            with col_c:
                st.markdown(f"""
                <div style='padding-top:8px'>
                    <span style='font-family:Share Tech Mono,monospace;font-size:0.85rem;color:{conf_color}'>{conf}/100{fire}</span>
                    <div class="conf-bar-wrap"><div class="conf-bar {conf_class}" style="width:{conf}%"></div></div>
                </div>""", unsafe_allow_html=True)
            with col_g:
                g_str = " &nbsp;·&nbsp; ".join(f'<span style="color:#444">{g}</span>' for g in gates) if gates else '<span style="color:#2a2a2a">no gates fired</span>'
                st.markdown(f"<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;padding-top:11px;line-height:1.5'>{g_str}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border:none;border-top:1px solid #111;margin:0.4rem 0'>", unsafe_allow_html=True)

    # ── Section B: the REAL 7-gate engine, on demand per coin ──────────────────
    st.markdown('<div class="st2">FULL 7-GATE SIGNAL (LIVE — RSI · SMC · MACD · BB · LSTM · FINBERT · RL)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    This calls the real <code>run_signal_engine()</code> via the <code>/explain</code> endpoint —
    the same engine <code>trader.py</code> uses to actually trade. It loads the LSTM model,
    fetches live FinBERT sentiment, and runs the RL agent, so a single coin can take up to
    ~45 seconds. Requires <code>api.py</code> + the <code>zoro</code> package running with model
    files present — not just a static file server.
    </div>""", unsafe_allow_html=True)

    sig_col1, sig_col2 = st.columns([1, 3])
    with sig_col1:
        full_scan_coin = st.selectbox("Coin", list(COINS.keys()), format_func=lambda x: COINS[x], key="full_scan_coin")
        run_full = st.button("⚔ RUN FULL SIGNAL ENGINE")

    if run_full:
        with st.spinner(f"Running LSTM + FinBERT + RL for {COINS[full_scan_coin]}… up to 45s"):
            full_sig = api_explain(full_scan_coin)
        if full_sig and "error" not in full_sig:
            direction_f = full_sig.get("direction", "FLAT")
            conf_f = full_sig.get("confidence", 0)
            price_f = float(full_sig.get("price", 0))
            gates_f = full_sig.get("gates", [])
            dir_color_f = "#5FD98F" if direction_f == "LONG" else "#C1554A" if direction_f == "SHORT" else "#888"
            st.markdown(f"""
            <div class="mc" style="border-top-color:{dir_color_f}">
                <div class="mc-label">{COINS[full_scan_coin]} — FULL ENGINE RESULT</div>
                <div class="mc-value" style="color:{dir_color_f};font-size:1.3rem">{direction_f} @ ${price_f:,.2f} &nbsp;·&nbsp; {conf_f}/100</div>
                <div class="mc-sub">{" &nbsp;·&nbsp; ".join(gates_f) if gates_f else "no gates fired"}</div>
            </div>""", unsafe_allow_html=True)
            explanation_f = full_sig.get("human_explanation", "")
            if explanation_f:
                st.markdown(f'<div class="info-box">{explanation_f}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warn-box">
            No response from the full signal engine. Make sure <code>uvicorn api:app --port 8000</code>
            is running and the LSTM model / RL agent files are present alongside it.
            </div>""", unsafe_allow_html=True)

    # Gate weight table
    st.markdown('<div class="st2">GATE WEIGHTS (from zoro/signals.py)</div>', unsafe_allow_html=True)
    gate_df = pd.DataFrame([
        ["1","RSI (25/75)","Oversold / Overbought","±20 pts"],
        ["2","SMC / SMA Structure","Trend alignment","±10 pts"],
        ["3","MACD Histogram","Momentum direction","±10 pts"],
        ["4","Bollinger Bands","Volatility extremes","±10 pts"],
        ["5","LSTM Neural Net","4H price prediction","±20 pts"],
        ["6","FinBERT Sentiment","News NLP score","±10 pts (±10 max)"],
        ["7","RL PPO Agent","Reinforcement signal","±10 pts"],
    ], columns=["#","Gate","Signal","Weight"])
    st.dataframe(gate_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PRICE CHART
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown('<div class="st2">PRICE + INDICATORS</div>', unsafe_allow_html=True)

    col_sel, col_period = st.columns([2,3])
    with col_sel:
        selected = st.selectbox("COIN", list(COINS.keys()), format_func=lambda x: COINS[x], key="chart_coin")

    _d2 = all_data.get(selected)
    df = _d2 if (_d2 is not None and not _d2.empty) else indicators(fetch_data(selected))

    if df is not None and not df.empty:
        # Stat bar
        r = df.iloc[-1]
        price = r["Close"]; rsi = r["RSI"]; atr = r["ATR"]
        bb_pos = r["BB_Pos"]; macd_h = r["MACD_Hist"]
        prev = df["Close"].iloc[-2]
        pct = (price-prev)/prev*100

        sc1,sc2,sc3,sc4,sc5,sc6 = st.columns(6)
        stat_items = [
            (sc1,"PRICE",f"${price:,.2f}",""),
            (sc2,"CHANGE",f"{'+' if pct>=0 else ''}{pct:.2f}%","g" if pct>=0 else "r"),
            (sc3,"RSI",f"{rsi:.1f}","r" if rsi>70 else "g" if rsi<30 else ""),
            (sc4,"ATR",f"${atr:.2f}",""),
            (sc5,"BB POS",f"{bb_pos:.2f}",""),
            (sc6,"MACD HIST",f"{macd_h:+.4f}","g" if macd_h>0 else "r"),
        ]
        for col,(label,val,cls) in zip([sc1,sc2,sc3,sc4,sc5,sc6], [(x[1],x[2],x[3]) for x in stat_items]):
            with col:
                st.markdown(f"""
                <div class="mc" style="padding:0.6rem 0.8rem">
                    <div class="mc-label">{label}</div>
                    <div class="mc-value {cls}" style="font-size:1.1rem">{val}</div>
                </div>""", unsafe_allow_html=True)

        # Main chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            row_heights=[0.6,0.2,0.2], vertical_spacing=0.01)

        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            increasing_line_color="#5FD98F", decreasing_line_color="#C1554A",
            increasing_fillcolor="#003d1f", decreasing_fillcolor="#3d0000",
            name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], line=dict(color="#ffd700",width=1), name="SMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], line=dict(color="#555",width=1,dash="dot"), name="SMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Up"], line=dict(color="rgba(76,138,99,0.13)",width=1), name="BB Upper",
                                 fill=None), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lo"], line=dict(color="rgba(76,138,99,0.13)",width=1), name="BB Lower",
                                 fill='tonexty', fillcolor='rgba(76,138,99,0.04)'), row=1, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="#C1554A",width=1.5), name="RSI"), row=2, col=1)
        fig.add_hline(y=75, line_color="#C1554A", line_dash="dot", opacity=0.3, row=2, col=1)
        fig.add_hline(y=25, line_color="#5FD98F", line_dash="dot", opacity=0.3, row=2, col=1)
        fig.add_hline(y=50, line_color="#333",    line_dash="dot", opacity=0.3, row=2, col=1)

        colors_m = ["#5FD98F" if v>=0 else "#C1554A" for v in df["MACD_Hist"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], marker_color=colors_m, name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], line=dict(color="#ffd700",width=1), name="MACD"), row=3, col=1)

        layout = plotly_base(480)
        layout.update(xaxis_rangeslider_visible=False)
        fig.update_layout(**layout)
        fig.update_yaxes(gridcolor="#111", showgrid=True, row=1, col=1)
        fig.update_yaxes(gridcolor="#111", showgrid=True, range=[0,100], row=2, col=1)
        fig.update_yaxes(gridcolor="#111", showgrid=True, row=3, col=1)
        for i in range(1,4):
            fig.update_xaxes(gridcolor="#111", showgrid=True, row=i, col=1)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not fetch price data.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BACKTEST
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    # ── Section A: REAL live paper-trading P&L (from /backtest — misleadingly
    # named in api.py, but its own docstring confirms it's live DB data) ───────
    st.markdown('<div class="st2">LIVE PAPER-TRADING P&L (REAL — FROM POSTGRESQL, NOT A SIMULATION)</div>', unsafe_allow_html=True)
    live_bt = api_backtest()
    if live_bt and live_bt.get("coins"):
        st.markdown(f'<span class="live-pill"><span class="live-dot" style="width:6px;height:6px"></span>LIVE — generated {live_bt.get("generated_at","")[:19]}</span>', unsafe_allow_html=True)
        live_bt_df = pd.DataFrame(live_bt["coins"])
        st.dataframe(live_bt_df, width='stretch', hide_index=True)
    else:
        st.markdown("""
        <div class="warn-box">
        No live P&L data yet — this needs <code>trader.py</code> running and writing trades
        to PostgreSQL. Until then there's nothing real to show here (no placeholder numbers
        are substituted).
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="st2">UPGRADE H — HISTORICAL BACKTEST ALL 5 COINS (1 YEAR, VECTORBT PIPELINE)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stale-box">
    NOTE: this table comes from the separate <code>backtest_runner.py</code> / vectorbt pipeline
    (Upgrade H) — a one-off historical simulation, distinct from the live P&L above and from the
    RL/LSTM retraining reports below. It has not been re-verified this session — treat it as an
    older, separate result set. (Its Sharpe formula uses the same √(252×24) annualization as the
    RL training bug fixed earlier — applied here to a full hourly equity curve, which is the
    statistically correct usage, but worth a quick sanity check if time allows.)
    </div>""", unsafe_allow_html=True)

    bt_raw = [
        ("ETH","ETH-USD",-15.3, 65,58.5,-45.3,-0.31,"⚠"),
        ("BTC","BTC-USD",-14.1, 70,54.3,-39.8,-0.28,"⚠"),
        ("SOL","SOL-USD",-12.0, 78,62.8,-46.5,-0.24,"⚠"),
        ("BNB","BNB-USD",+16.9, 71,64.8,-31.2,+0.41,"✅"),
        ("ADA","ADA-USD",-61.2, 75,53.3,-69.0,-0.89,"❌"),
    ]

    # Return chart
    coins_bt = [r[0] for r in bt_raw]
    returns_bt = [r[2] for r in bt_raw]
    colors_bt = ["#5FD98F" if v>=0 else "#C1554A" for v in returns_bt]

    fig_bt = go.Figure()
    fig_bt.add_trace(go.Bar(x=coins_bt, y=returns_bt, marker_color=colors_bt,
                            text=[f"{v:+.1f}%" for v in returns_bt],
                            textposition="outside",
                            textfont=dict(family="Share Tech Mono",color="#888",size=11)))
    fig_bt.add_hline(y=0, line_color="#333", line_width=1)
    layout_bt = plotly_base(250)
    layout_bt["yaxis"]["title"] = "Return %"
    layout_bt["yaxis"]["zeroline"] = True
    layout_bt["yaxis"]["zerolinecolor"] = "#333"
    fig_bt.update_layout(**layout_bt)
    st.plotly_chart(fig_bt, use_container_width=True)

    # Table
    bt_df = pd.DataFrame([{
        "Coin":r[0], "Return":f"{r[2]:+.1f}%",
        "Trades":r[3], "Win Rate":f"{r[4]:.1f}%",
        "Max DD":f"{r[5]:.1f}%", "Sharpe":f"{r[6]:.2f}", "Status":r[7]
    } for r in bt_raw])
    st.dataframe(bt_df, width='stretch', hide_index=True)

    st.markdown("""
    <div class="info-box">
    📌 Long-only weakness fixed in Upgrade F with short selling support.<br>
    📌 Why 53.3% LSTM accuracy and not 90%? — A consistent directional edge with risk management
    can be profitable; 90%+ on real market data would itself be a red flag for overfitting or leakage.
    </div>""", unsafe_allow_html=True)

    # Walk-forward — REAL data from the two report files
    st.markdown('<div class="st2">WALK-FORWARD VALIDATION (REAL — FROM RETRAIN REPORTS)</div>', unsafe_allow_html=True)

    col_wf1, col_wf2 = st.columns(2)
    with col_wf1:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#555;letter-spacing:2px;margin-bottom:0.4rem">LSTM — 3 WINDOWS</div>', unsafe_allow_html=True)
        lstm_wf_df = pd.DataFrame([
            {"Window": f"Window {i+1}", "Accuracy": f"{v:.1f}%"}
            for i, v in enumerate(LSTM_RESULTS["walk_forward"])
        ])
        st.dataframe(lstm_wf_df, width='stretch', hide_index=True)
        spread_lstm = max(LSTM_RESULTS["walk_forward"]) - min(LSTM_RESULTS["walk_forward"])
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#888">Spread: {spread_lstm:.1f} pts — reasonably consistent</div>', unsafe_allow_html=True)

    with col_wf2:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#555;letter-spacing:2px;margin-bottom:0.4rem">RL — PER-COIN SHARPE CONSISTENCY</div>', unsafe_allow_html=True)
        rl_wf_df = pd.DataFrame([
            {"Coin": c.replace("-USD",""), "Spread": f"{v['spread']:.2f}", "Flag": v["flag"]}
            for c, v in RL_RESULTS["walk_forward"].items()
        ])
        st.dataframe(rl_wf_df, width='stretch', hide_index=True)
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#C1554A">Overall: consistent = NO (BTC, ADA flagged CHECK)</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RL AGENT
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown('<div class="st2">PPO REINFORCEMENT LEARNING AGENT &nbsp; (training-time evaluation, not live)</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1,1])
    with col_left:
        for label,val,cls,sub in [
            ("ALGORITHM","PPO (Proximal Policy Optimization)","","Stable-Baselines3"),
            ("TRAINING STEPS",f"{RL_RESULTS['steps']:,}","g","single training run"),
            ("WIN RATE (AVG, FINAL EVAL)",f"{RL_WIN_AVG:.1f}%","y","range 68.2%–97.6% by coin"),
            ("SHARPE (AVG, FINAL EVAL)",f"{RL_SHARPE_AVG:.2f}","y",f"range {RL_SHARPE_MIN:.2f}–{RL_SHARPE_MAX:.2f}"),
            ("ACTION SPACE","BUY · SELL · HOLD","","discrete 3"),
        ]:
            st.markdown(f"""
            <div class="mc">
                <div class="mc-label">{label}</div>
                <div class="mc-value {cls}" style="font-size:{'1rem' if len(val)>10 else '1.4rem'}">{val}</div>
                <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="stale-box">
        ⚠️ Win rates of 68–98% are unusually high for a real trading strategy and are
        flagged here rather than presented as an unqualified success — see the
        walk-forward consistency panel below before citing this number anywhere formal.
        </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="st2">STATE SPACE (10 FEATURES)</div>', unsafe_allow_html=True)
        obs_df = pd.DataFrame([
            ["RSI","Momentum oscillator 0-100"],
            ["MACD","Trend momentum signal"],
            ["BB_Position","Volatility band position 0-1"],
            ["ATR","Normalised average true range"],
            ["SMA_Ratio","SMA20/SMA50 ratio"],
            ["LSTM_prob","Neural net directional prob"],
            ["Sentiment","FinBERT NLP score -1 to 1"],
            ["Volume_Ratio","Volume vs 20-period MA"],
            ["PnL","Current position PnL"],
            ["Position","Current pos: -1, 0, +1"],
        ], columns=["Feature","Description"])
        st.dataframe(obs_df, width='stretch', hide_index=True)

        st.markdown('<div class="st2">REWARD FUNCTION</div>', unsafe_allow_html=True)
        st.code("reward = sharpe_ratio   # per report: 'Reward: Sharpe ratio'", language="python")

    # Final evaluation — real per-coin table
    st.markdown('<div class="st2">FINAL MODEL — PER-COIN EVALUATION (REAL, SINGLE WINDOW)</div>', unsafe_allow_html=True)
    final_df = pd.DataFrame([
        {"Coin": c.replace("-USD",""), "Win Rate": f"{v['win']:.1f}%",
         "Sharpe": f"{v['sharpe']:.3f}", "Trades": v["trades"]}
        for c, v in RL_RESULTS["final_eval"].items()
    ])
    st.dataframe(final_df, width='stretch', hide_index=True)

    fig_final = go.Figure(go.Bar(
        x=[c.replace("-USD","") for c in RL_RESULTS["final_eval"]],
        y=[v["win"] for v in RL_RESULTS["final_eval"].values()],
        marker_color="#C1554A",
        text=[f"{v['win']:.1f}%" for v in RL_RESULTS["final_eval"].values()],
        textposition="outside",
        textfont=dict(family="Share Tech Mono", color="#888", size=11),
    ))
    l_final = plotly_base(240)
    fig_final.update_layout(**l_final)
    st.plotly_chart(fig_final, width='stretch')

    # Walk-forward consistency — the honest counterpart
    st.markdown('<div class="st2">WALK-FORWARD CONSISTENCY — PER-COIN SHARPE ACROSS 3 WINDOWS</div>', unsafe_allow_html=True)
    wf_detail_df = pd.DataFrame([
        {"Coin": c.replace("-USD",""),
         "Sharpe W1": v["sharpes"][0], "Sharpe W2": v["sharpes"][1], "Sharpe W3": v["sharpes"][2],
         "Spread": f"{v['spread']:.2f}", "Flag": v["flag"]}
        for c, v in RL_RESULTS["walk_forward"].items()
    ])
    st.dataframe(wf_detail_df, width='stretch', hide_index=True)
    st.markdown(f"""
    <div class="warn-box">
    Overall: <strong style="color:#C1554A">consistent = NO</strong> — BTC-USD (spread 2.20) and
    ADA-USD (spread 0.76) show sharpe swings across windows large enough to be flagged [CHECK].
    ETH, SOL, and BNB are [OK]. This is stated directly rather than smoothed over, per project policy
    on this dashboard.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SHAP + TRADE LOG (LIVE — pulls from FastAPI)
# ══════════════════════════════════════════════════════════════════════════════
with t6:
    # ── Bot status bar ────────────────────────────────────────────────────────
    bot_status = api_status()
    if bot_status and bot_status.get("status") == "running":
        open_pos = bot_status.get("open_positions", 0)
        coins_open = ", ".join(bot_status.get("coins_tracked", [])) or "none"
        st.markdown(f"""
        <div class="info-box" style="margin-bottom:0.8rem">
            ⚔️ <strong style="color:#5FD98F">TRADER ONLINE</strong> &nbsp;·&nbsp;
            Open positions: <strong style="color:#ffd700">{open_pos}</strong> &nbsp;·&nbsp;
            Coins: <strong style="color:#ffd700">{coins_open}</strong>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warn-box" style="margin-bottom:0.8rem">
            ⚠️ trader.py not running — start it to see live signals.
            Run: <code>python trader.py</code>
        </div>""", unsafe_allow_html=True)

    col_shap, col_log = st.columns([1,1])

    with col_shap:
        # ── Coin selector ─────────────────────────────────────────────────────
        st.markdown('<div class="st2">SHAP EXPLAINABILITY — SELECT COIN</div>', unsafe_allow_html=True)
        shap_coin = st.selectbox(
            "Explain signal for:", list(COINS.keys()),
            format_func=lambda x: COINS[x],
            key="shap_coin_selector"
        )
        if st.button("🔍 FETCH LIVE EXPLANATION"):
            st.cache_data.clear()

        shap_data = api_explain(shap_coin)

        if shap_data and "error" not in shap_data:
            direction_s  = shap_data.get("direction", shap_data.get("action", "FLAT"))
            price_s      = float(shap_data.get("price", 0))
            conf_s       = int(shap_data.get("confidence", 0))
            rsi_s        = float(shap_data.get("rsi", 0))
            sentiment_s  = float(shap_data.get("sentiment", 0))
            lstm_s       = float(shap_data.get("lstm_prob", 0.5))

            dir_color = "#5FD98F" if direction_s == "LONG" else "#C1554A"
            st.markdown(f"""
            <div class="mc" style="border-top-color:{dir_color}">
                <div class="mc-label">{shap_coin} — LIVE SIGNAL</div>
                <div class="mc-value" style="color:{dir_color};font-size:1.3rem">{direction_s} @ ${price_s:,.2f}</div>
                <div class="mc-sub">CONF {conf_s}/100 &nbsp;·&nbsp; RSI {rsi_s:.1f} &nbsp;·&nbsp; LSTM {lstm_s:.1%} &nbsp;·&nbsp; SENT {sentiment_s:+.3f}</div>
            </div>""", unsafe_allow_html=True)

            # Human explanation
            explanation = shap_data.get("human_explanation","")
            if explanation:
                st.markdown(f"""
                <div class="warn-box" style="margin-top:0.8rem">
                    🤖 <strong style="color:#ffd700">WHY THIS SIGNAL:</strong><br>
                    {explanation}
                </div>""", unsafe_allow_html=True)

            # Feature contributions
            features = shap_data.get("feature_contributions", [])
            if features:
                st.markdown('<div style="margin-top:1rem;font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#555;letter-spacing:2px">FEATURE IMPORTANCE</div>', unsafe_allow_html=True)
                for fc in features:
                    pct   = fc.get("pct", 0)
                    label = fc.get("label", "")
                    desc  = fc.get("description", "")
                    color = "shap-bar-neg" if fc.get("bullish", False) else "shap-bar-pos"
                    st.markdown(f"""
                    <div class="shap-row">
                        <div class="shap-label">{label}</div>
                        <div class="{color}" style="width:{int(pct*2)}px"></div>
                        <div class="shap-pct">{pct:.1f}%</div>
                        <div style="font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#333;flex:1">{desc}</div>
                    </div>""", unsafe_allow_html=True)

            # Gates fired
            gates_list = shap_data.get("gates", [])
            if gates_list:
                st.markdown('<div style="margin-top:0.8rem;font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#555;letter-spacing:2px">GATES FIRED</div>', unsafe_allow_html=True)
                for g in gates_list:
                    st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:0.72rem;color:#444;padding:2px 0">▸ {g}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warn-box">
                No live signal for {shap_coin} yet.<br>
                Make sure <code>trader.py</code> and <code>uvicorn api:app --port 8000</code> are both running.
            </div>""", unsafe_allow_html=True)

    with col_log:
        st.markdown('<div class="st2">TRADE LOG — ALL COINS</div>', unsafe_allow_html=True)

        trades, trades_live = api_trades(limit=20)

        # ── Live vs stale indicator ─────────────────────────────────────────
        if trades_live:
            st.markdown('<span class="live-pill"><span class="live-dot" style="width:6px;height:6px"></span>LIVE — from running trader.py</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="stale-pill">⏸ STALE SNAPSHOT — reading zoro_trade_log.json (trader.py API unreachable)</span>', unsafe_allow_html=True)

        # ── PnL Summary Stats ─────────────────────────────────────────────────
        if trades:
            _closed = [t for t in trades if t.get("pnl") is not None]
            _total_trades = len(trades)
            _total_pnl = sum(float(t["pnl"]) for t in _closed) if _closed else 0.0
            _wins = sum(1 for t in _closed if float(t["pnl"]) > 0)
            _win_rate = (_wins / len(_closed) * 100) if _closed else 0.0
            _pnl_color = "g" if _total_pnl >= 0 else "r"
            _pnl_sign  = "+" if _total_pnl >= 0 else ""

            ps1, ps2, ps3 = st.columns(3)
            with ps1:
                st.markdown(f"""
                <div class="mc" style="padding:0.5rem 0.8rem">
                    <div class="mc-label">TOTAL TRADES</div>
                    <div class="mc-value" style="font-size:1.1rem">{_total_trades}</div>
                </div>""", unsafe_allow_html=True)
            with ps2:
                st.markdown(f"""
                <div class="mc" style="padding:0.5rem 0.8rem">
                    <div class="mc-label">TOTAL PnL</div>
                    <div class="mc-value {_pnl_color}" style="font-size:1.1rem">{_pnl_sign}${_total_pnl:.2f}</div>
                </div>""", unsafe_allow_html=True)
            with ps3:
                st.markdown(f"""
                <div class="mc" style="padding:0.5rem 0.8rem">
                    <div class="mc-label">WIN RATE</div>
                    <div class="mc-value {'g' if _win_rate>=50 else 'r'}" style="font-size:1.1rem">{_win_rate:.1f}%</div>
                </div>""", unsafe_allow_html=True)
        if trades:
            for tr in reversed(trades[-10:]):
                action = tr.get("action","?")
                coin   = tr.get("coin", tr.get("symbol","?"))
                price  = float(tr.get("price", 0))
                conf   = tr.get("confidence", 0)
                rsi    = float(tr.get("rsi", 0))
                rl     = tr.get("rl_signal","?")
                ts     = str(tr.get("timestamp",""))[:19]
                sl     = float(tr.get("stop_loss") or 0)
                pnl    = tr.get("pnl")
                border = "#5FD98F" if action == "LONG" else "#C1554A"
                pnl_str = f"PnL: {float(pnl):+.2f}" if pnl is not None else "PnL: OPEN"
                st.markdown(f"""
                <div class="trade-row" style="border-left-color:{border}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="color:{border};font-size:0.8rem;letter-spacing:2px">{action}</span>
                        <span style="color:#555;font-size:0.68rem">{ts}</span>
                    </div>
                    <div style="font-size:0.85rem;color:#aaa;margin:2px 0">{coin} &nbsp;@&nbsp; ${price:,.2f}</div>
                    <div style="font-size:0.68rem;color:#444">
                        CONF {conf}/100 &nbsp;·&nbsp; RSI {rsi:.1f} &nbsp;·&nbsp; RL {rl} &nbsp;·&nbsp; SL ${sl:,.2f} &nbsp;·&nbsp; {pnl_str}
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#0D120E;border:1px solid #1A241D;padding:2.5rem;text-align:center;border-radius:3px;margin-top:1rem">
                <div style="font-family:Share Tech Mono,monospace;color:#2a2a2a;font-size:0.85rem">
                    NO TRADES YET<br><br>
                    <span style="font-size:0.7rem;color:#1A241D">
                        Run <code style="color:#333">python trader.py</code> to begin paper trading.<br>
                        Trades will appear here automatically.
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

        # Raw latest trade JSON
        st.markdown('<div class="st2">LAST TRADE — RAW JSON</div>', unsafe_allow_html=True)
        if trades:
            st.json(trades[-1])
        else:
            st.code("""{
  "timestamp": "2026-05-30 16:15:55",
  "symbol":    "BNB-USD",
  "action":    "SHORT",
  "price":     674.30,
  "rsi":       99.26,
  "confidence": 73,
  "rl_signal": "SELL",
  "lstm_prob": 0.4912,
  "stop_loss": 681.17,
  "take_profit": 660.55,
  "pnl":       null
}""", language="json")

# ── Auto-refresh trigger (non-blocking — doesn't freeze the UI/dropdowns) ─────
if auto_refresh:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="zoro_autorefresh")
