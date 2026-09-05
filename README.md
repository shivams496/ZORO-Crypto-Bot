# ⚔️ ZORO — Crypto AI Trading Bot

> **RL + LSTM + FinBERT · 5-Coin Paper Trader**

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-green)](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)
[![GitHub](https://img.shields.io/badge/GitHub-ZORO--Crypto--Bot-red)](https://github.com/shivams496/ZORO-Crypto-Bot)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Status](https://img.shields.io/badge/Status-Paper%20Trading%20Live-brightgreen)

---

## Overview

ZORO is an automated crypto paper trading system that combines **Reinforcement Learning**, **LSTM neural networks**, and **FinBERT sentiment analysis** to generate trading signals for five cryptocurrencies on Binance Testnet.

The system was built incrementally across multiple upgrade phases — from an initial RSI-based signal script to a full pipeline with a FastAPI backend, PostgreSQL persistence, SHAP-based explainability, and a live Hugging Face Spaces deployment.

---

## Live Demo

🟢 **Running on Hugging Face Spaces:**
👉 [huggingface.co/spaces/shivams496/Zoro-crypto-bot](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)

**Included in the demo:**

- Live signal generation with confidence scoring (e.g. BNB SHORT signal, RSI 99.3, confidence 73/100)
- LSTM walk-forward validation across multiple test windows (see `retrain_report.txt`)
- SHAP explainability for individual trading decisions
- Strategy comparison: RL Agent vs LSTM vs RSI vs Buy-and-Hold

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ZORO SYSTEM                           │
├──────────────┬──────────────┬────────────────────────────┤
│   Data Layer │   AI Layer   │      Execution Layer        │
│              │              │                              │
│  yfinance    │  LSTM 3-layer│  7-Gate Signal Engine        │
│  Binance WS  │  PPO RL Agent│  RSI 25/75 thresholds        │
│  FinBERT RSS │  SHAP Explain│  ATR stop-loss               │
│  PostgreSQL  │  53% accuracy│  Trailing stop 1.5%          │
├──────────────┴──────────────┴────────────────────────────┤
│                   API + Dashboard                          │
│   FastAPI :8000  ·  Streamlit KATANA  ·  Hugging Face      │
└─────────────────────────────────────────────────────────┘
```

---

## Results

### Model Performance

| Metric           | Value  | Notes                                     |
| ---------------- | ------ | ------------------------------------------ |
| LSTM Accuracy    | 53.3%  | Walk-forward validated, no lookahead bias |
| RL Avg Win Rate  | 85.3%  | Across 5 coins, PPO, 300k training steps  |
| RL Avg Sharpe    | 1.21   | Per-trade Sharpe ratio                    |
| Signal Threshold | 70/100 | 7-gate confidence score                   |
| Coins Traded     | 5      | ETH, BTC, SOL, BNB, ADA                   |

> LSTM accuracy is evaluated against a 50% random-guess baseline for binary up/down prediction. A consistent edge above that baseline, paired with disciplined risk management, is the target — walk-forward validation across multiple time windows confirms the result isn't specific to one historical period.

### RL Agent — Per-Coin Evaluation

| Coin | Win Rate | Sharpe | Trades |
| ---- | -------- | ------ | ------ |
| ETH  | 88.1%    | 1.211  | 67     |
| BTC  | 88.1%    | 1.105  | 42     |
| SOL  | 84.4%    | 0.979  | 45     |
| BNB  | 97.6%    | 2.465  | 84     |
| ADA  | 68.2%    | 0.277  | 66     |

Sharpe is calculated per-trade (not annualized), which is the more conservative and defensible metric given the variable trade frequency across coins and time windows.

### Earlier Backtest (vectorbt pipeline)

| Coin    | Return     | Trades | Win Rate | Max Drawdown |
| ------- | ---------- | ------ | -------- | ------------- |
| ETH     | -15.3%     | 65     | 58.5%    | -45.3%        |
| BTC     | -14.1%     | 70     | 54.3%    | -39.8%        |
| SOL     | -12.0%     | 78     | 62.8%    | -46.5%        |
| **BNB** | **+16.9%** | 71     | 64.8%    | -31.2%        |
| ADA     | -61.2%     | 75     | 53.3%    | -69.0%        |

> Produced by a separate vectorbt-based backtest (`backtest_runner.py`) from an earlier development phase; reported independently of the RL agent evaluation above.

---

## 7-Gate Signal Engine

Every trade requires passing a combined confidence score of at least 70/100:

| Gate                 | Signal               | Weight  |
| --------------------- | --------------------- | -------- |
| RSI (25/75)          | Oversold/Overbought  | ±20 pts |
| SMC / Price vs SMA20 | Structure             | ±10 pts |
| MACD Histogram       | Momentum              | ±10 pts |
| Bollinger Bands      | Volatility            | ±15 pts |
| LSTM Neural Net      | 4H prediction         | ±15 pts |
| FinBERT Sentiment    | News NLP              | ±10 pts |
| Volume Ratio         | Confirmation          | ±5 pts  |

---

## Development History

| Stage | Feature                                          |
| ----- | ------------------------------------------------- |
| A     | LSTM 3-layer neural network (60h sequence)       |
| B     | Backtesting with vectorbt (1yr ETH+BTC)          |
| C     | Paper trading on Binance Testnet                 |
| D     | PPO reinforcement learning agent                 |
| E     | KATANA dashboard (Streamlit)                     |
| F     | Short selling, ATR stop-loss, trailing stop      |
| G     | Telegram alerts, 5-coin expansion                |
| H     | Full backtest across all 5 coins                 |
| I     | RL evaluation pipeline refinement and retraining |

---

## Project Structure

```
ZORO-Crypto-Bot/
├── zoro/                    # Core Python package
│   ├── config.py            # Coins, thresholds, settings
│   ├── data.py              # yfinance + indicator computation
│   ├── signals.py           # 7-gate signal engine
│   ├── lstm_model.py        # LSTM training + inference
│   ├── rl_agent.py          # PPO agent wrapper
│   ├── sentiment.py         # FinBERT NLP pipeline
│   ├── explainability.py    # SHAP explanations
│   ├── database.py          # PostgreSQL (SQLAlchemy)
│   └── alerts.py            # Telegram + Email
├── api.py                   # FastAPI backend (:8000)
├── trader.py                # Main trading loop
├── dashboard.py             # Streamlit KATANA terminal
├── explain_dashboard.html   # SHAP explainability UI
├── train_rl_agent.py        # PPO training script
├── retrain_lstm.py          # LSTM retraining script
├── backtest_runner.py       # Vectorbt backtest runner
├── gym_env.py                # Custom Gym environment
├── Dockerfile                # Container config
├── docker-compose.yml         # PostgreSQL + app stack
├── requirements.txt           # All dependencies
└── .env.example                # Credentials template
```

---

## Quick Start

### Option 1 — Hugging Face (no setup required)

Visit the live demo directly: [huggingface.co/spaces/shivams496/Zoro-crypto-bot](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)

### Option 2 — Local with Docker

```bash
git clone https://github.com/shivams496/ZORO-Crypto-Bot.git
cd ZORO-Crypto-Bot
cp .env.example .env        # Add your API keys
docker-compose up --build   # Starts app + PostgreSQL
```

### Option 3 — Local without Docker

```bash
git clone https://github.com/shivams496/ZORO-Crypto-Bot.git
cd ZORO-Crypto-Bot
pip install -r requirements.txt
cp .env.example .env        # Add your API keys

# Run the dashboard
streamlit run dashboard.py

# Or run the full trading bot
python trader.py
```

---

## Environment Variables

Create a `.env` file (do not commit this):

```env
BINANCE_TESTNET_API_KEY=your_key_here
BINANCE_TESTNET_SECRET=your_secret_here
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://zoro:zoro@localhost:5432/zorodb
```

---

## Tech Stack

| Layer      | Technology                                       |
| ---------- | ------------------------------------------------- |
| Language   | Python 3.12                                      |
| AI/ML      | TensorFlow/Keras, Stable-Baselines3 (PPO), SHAP  |
| NLP        | FinBERT (HuggingFace Transformers)               |
| Data       | yfinance, Binance WebSocket, VADER               |
| Backend    | FastAPI, SQLAlchemy, PostgreSQL                  |
| Dashboard  | Streamlit (KATANA theme)                         |
| Deployment | Docker, Hugging Face Spaces                      |
| Exchange   | Binance Testnet (paper trading only)             |

---

## Disclaimer

This is a paper trading project built for educational purposes. No real funds are used or at risk. Past backtest performance does not guarantee future results. Cryptocurrency trading carries significant risk.

---

**Builder:** Shivam · **Exchange:** Binance Testnet only
