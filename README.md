---
title: Zoro Crypto Bot
sdk: docker
app_port: 7860
---

# ⚔️ ZORO — Crypto AI Trading Bot

> **RL + LSTM + FinBERT · 5-Coin Paper Trader · Phase 4**

[![Live Demo](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-green)](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)
[![GitHub](https://img.shields.io/badge/GitHub-ZORO--Crypto--Bot-red)](https://github.com/shivams496/Zoro-crypto-bot)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Paper%20Trading%20Live-brightgreen)](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)

---

## Overview

ZORO is an automated crypto **paper trading** system that combines a Reinforcement Learning agent (PPO), an LSTM price-direction model, and FinBERT news sentiment into a single signal engine, monitoring 5 coins in real time.

It is built as a full-stack ML system, not a script: FastAPI backend, SQLite persistence, SHAP-based explainability, and a live Streamlit terminal deployed on Hugging Face Spaces.

**All trades are simulated (paper trading). No real orders are placed on any exchange, and no real funds are used or at risk anywhere in this project.** Binance Testnet API credentials are present in configuration for planned future order-execution work but are not yet wired into the trading loop.

---

## Live Demo

🟢 **[huggingface.co/spaces/shivams496/Zoro-crypto-bot](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)**

The dashboard reads directly from live model outputs and the real trade database — not static placeholders. You'll see:

- Live signal generation across 5 coins via the 7-gate confidence engine
- Actual LSTM and RL walk-forward validation results (below)
- SHAP explainability for every fired signal
- Real, timestamped paper trade history

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                          ZORO SYSTEM                          │
├───────────────────┬───────────────────┬───────────────────────┤
│     Data Layer     │      AI Layer      │    Execution Layer    │
│                     │                    │                       │
│  yfinance           │  LSTM (3-layer)    │  7-Gate Signal Engine │
│  Binance WebSocket  │  PPO RL Agent      │  RSI 25 / 75          │
│  FinBERT (news)     │  SHAP explainer    │  ATR stop-loss        │
│  PostgreSQL         │                    │  Trailing stop 1.5%   │
├───────────────────┴───────────────────┴───────────────────────┤
│                     API + Dashboard Layer                      │
│      FastAPI (:8000)   ·   Streamlit "Santoryu" Terminal        │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Results (Verified Against Source Reports)

Every number below is pulled directly from `retrain_report.txt` and `rl_train_report.txt` in this repo — nothing here is estimated or hardcoded into the dashboard.

### LSTM — Direction Prediction

| Metric | Value |
|---|---|
| Train accuracy | 50.0% |
| Validation accuracy | 49.8% |
| **Test accuracy** | **53.3%** |
| Walk-forward window 1 | 55.3% |
| Walk-forward window 2 | 54.9% |
| Walk-forward window 3 | 49.7% |
| Sequence length | 60 candles |
| Prediction horizon | 4 hours |
| Train / Val / Test split | 70 / 15 / 15 |

Scaler fit on the training split only — no lookahead bias. A ~53–55% directional edge is modest by design; this is a 4h binary direction call on crypto, where anything durably above 50% is a real, non-trivial signal rather than noise.

### RL Agent (PPO) — Per-Coin Evaluation

PPO trained for 300,000 steps across a 10-feature observation space (RSI, MACD, Bollinger Bands, trend, volatility, sentiment, momentum, LSTM output, daily return, ATR), 3 discrete actions (HOLD / BUY / SELL), Sharpe-ratio reward.

| Coin | Win Rate | Sharpe | Trades |
|---|---|---|---|
| BNB-USD | 97.6% | 2.465 | 84 |
| ETH-USD | 88.1% | 1.211 | 67 |
| BTC-USD | 88.1% | 1.105 | 42 |
| SOL-USD | 84.4% | 0.979 | 45 |
| ADA-USD | 68.2% | 0.277 | 66 |

**Known limitation — flagged, not hidden:** walk-forward consistency across the 3 validation windows returned `consistent = NO`. Window 2 produced a flat 0.00 Sharpe across all 5 coins, which does not fit the pattern of the other two windows and has not yet been root-caused (leading hypothesis: an empty-trade edge case in that window's date range). This is disclosed here deliberately rather than suppressed — the per-coin final-model numbers above are real, but should be read alongside this open question, not instead of it.

---

## 7-Gate Signal Engine

A trade only fires once a composite confidence score crosses **70/100**:

| Gate | Signal | Weight |
|---|---|---|
| RSI (25 / 75) | Oversold / Overbought | ±20 |
| Price vs SMA-20 | Market structure | ±10 |
| MACD Histogram | Momentum | ±10 |
| Bollinger Bands | Volatility | ±15 |
| LSTM (4h prediction) | Direction | ±15 |
| FinBERT | News sentiment | ±10 |
| Volume Ratio | Confirmation | ±5 |

---

## Backtest — Upgrade H (Legacy Pipeline)

This table comes from an earlier vectorbt-based backtest pipeline, separate from the RL/LSTM system above. It has **not** been re-audited in the current phase and is presented as-is for historical reference, not as a claim about the current model.

| Coin | Return | Trades | Win Rate | Max Drawdown |
|---|---|---|---|---|
| **BNB** | **+16.9%** | 71 | 64.8% | −31.2% |
| ETH | −15.3% | 65 | 58.5% | −45.3% |
| BTC | −14.1% | 70 | 54.3% | −39.8% |
| SOL | −12.0% | 78 | 62.8% | −46.5% |
| ADA | −61.2% | 75 | 53.3% | −69.0% |

Long-only bias in this run was later addressed with short-selling support (see Upgrade F below), but that fix was not re-run through this specific backtest.

---

## Development History

| Phase | Feature | Status |
|---|---|---|
| A | LSTM 3-layer network (60h sequence) | ✅ |
| B | vectorbt backtesting (1yr, ETH + BTC) | ✅ |
| C | Paper trading on Binance Testnet | ✅ |
| D | PPO RL agent (300k steps) | ✅ |
| E | Streamlit dashboard | ✅ |
| F | Short selling + ATR stop-loss + trailing stop | ✅ |
| G | Telegram alerts + 5-coin expansion | ✅ |
| H | Full 5-coin legacy backtest | ✅ |
| — | RL/LSTM retraining with corrected Sharpe calc | ✅ |
| — | Live dashboard wired to real report/API data (no hardcoded metrics) | ✅ |

---

## Project Structure

```
Zoro-crypto-bot/
├── zoro/
│   ├── config.py            # Coins, thresholds, settings
│   ├── data.py              # yfinance + indicator computation
│   ├── signals.py           # 7-gate signal engine
│   ├── lstm_model.py        # LSTM training + inference
│   ├── rl_agent.py          # PPO agent wrapper
│   ├── sentiment.py         # FinBERT pipeline
│   ├── explainability.py    # SHAP explanations
│   ├── database.py          # PostgreSQL (SQLAlchemy)
│   └── alerts.py            # Telegram + email
├── api.py                   # FastAPI backend (:8000)
├── trader.py                # Main trading loop
├── dashboard.py             # Streamlit terminal (:7860 public)
├── explain_dashboard.html   # SHAP explainability UI
├── train_rl_agent.py        # PPO training script
├── retrain_lstm.py          # LSTM retraining script
├── backtest_runner.py       # vectorbt backtest runner
├── gym_env.py                # Custom Gym environment
├── retrain_report.txt        # LSTM training report (source of truth)
├── rl_train_report.txt       # RL training report (source of truth)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Quick Start

### Option 1 — Hosted demo (no setup)
Visit **[huggingface.co/spaces/shivams496/Zoro-crypto-bot](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)**.

### Option 2 — Local, with Docker
```bash
git clone https://github.com/shivams496/Zoro-crypto-bot.git
cd Zoro-crypto-bot
cp .env.example .env        # add your API keys
docker-compose up --build   # app + PostgreSQL
```

### Option 3 — Local, without Docker
```bash
git clone https://github.com/shivams496/Zoro-crypto-bot.git
cd Zoro-crypto-bot
pip install -r requirements.txt
cp .env.example .env

streamlit run dashboard.py   # dashboard only
python trader.py             # or the full trading loop
```

---

## Environment Variables

Create a `.env` file (never commit this — see `.gitignore`):

```
BINANCE_TESTNET_API_KEY=your_key_here
BINANCE_TESTNET_SECRET=your_secret_here
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://zoro:zoro@localhost:5432/zorodb
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| ML / RL | TensorFlow/Keras, Stable-Baselines3 (PPO), SHAP |
| NLP | FinBERT (HuggingFace Transformers) |
| Data | yfinance, Binance WebSocket, VADER |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Dashboard | Streamlit |
| Deployment | Docker, Hugging Face Spaces |
| Exchange | Binance Testnet (paper trading only) |

---

## Disclaimer

This is a **paper trading** project built for educational purposes. No real money is used or at risk. Past backtest and validation performance does not guarantee future results, and the open walk-forward consistency issue noted above should be read as an active limitation, not a resolved one. This is not financial advice.

---

**Builder:** Shivam · **Exchange:** Binance Testnet only · **Status:** Live paper-trading demo
