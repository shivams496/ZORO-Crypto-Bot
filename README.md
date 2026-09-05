# ⚔️ ZORO — Crypto AI Trading Bot

> **RL + LSTM + FinBERT · 5-Coin Paper Trader · Phase 4 Complete**

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-green)](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)
[![GitHub](https://img.shields.io/badge/GitHub-ZORO--Crypto--Bot-red)](https://github.com/shivams496/ZORO-Crypto-Bot)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Status](https://img.shields.io/badge/Status-Paper%20Trading%20Live-brightgreen)

---

## What is ZORO?

ZORO is a fully automated crypto paper trading bot that combines **Reinforcement Learning**, **LSTM neural networks**, and **FinBERT sentiment analysis** to generate trading signals for 5 cryptocurrencies on Binance Testnet.

Built from scratch across 8 upgrade phases — from a simple RSI script to a production-grade AI trading system with a FastAPI backend, PostgreSQL database, SHAP explainability, and live Hugging Face deployment.

---

## Live Demo

🟢 **Running now on Hugging Face Spaces:**
👉 [huggingface.co/spaces/shivams496/Zoro-crypto-bot](https://huggingface.co/spaces/shivams496/Zoro-crypto-bot)

**What you'll see:**

- Live BNB SHORT signal fired (RSI 99.3, conf 73/100)
- LSTM walk-forward validation across test windows (see `retrain_report.txt` for exact per-window figures)
- SHAP explainability — why the bot made each decision
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

## Key Results (Honest Numbers — Phase 2 Retraining)

| Metric           | Value  | Notes                                      |
| ---------------- | ------ | ------------------------------------------- |
| LSTM Accuracy    | 53.3%  | Walk-forward validated, no lookahead bias  |
| RL Avg Win Rate  | 85.3%  | Across 5 coins, PPO 300k steps             |
| RL Avg Sharpe    | 1.21   | Per-trade Sharpe, not annualized (honest)  |
| Signal Threshold | 70/100 | 7-gate confidence score                    |
| Coins Traded     | 5      | ETH, BTC, SOL, BNB, ADA                    |

> **Why 53% and not 90%?** Because 90% would be fake. Real crypto AI is hard. A consistent edge over the 50% random-guess baseline, combined with proper risk management, is what makes a strategy viable — walk-forward windows confirm this isn't overfitting to one historical period.

### RL Agent — Per-Coin Evaluation (Phase 2, honest Sharpe)

| Coin | Win Rate | Sharpe | Trades |
| ---- | -------- | ------ | ------ |
| ETH  | 88.1%    | 1.211  | 67     |
| BTC  | 88.1%    | 1.105  | 42     |
| SOL  | 84.4%    | 0.979  | 45     |
| BNB  | 97.6%    | 2.465  | 84     |
| ADA  | 68.2%    | 0.277  | 66     |

> Sharpe here is per-trade (not annualized). An earlier evaluation had a bug that over-annualized returns, producing impossible values (e.g. Sharpe of 873). These are the corrected, honest figures. Walk-forward validation also showed one training window where the agent placed zero trades across all coins — noted here for transparency, not yet root-caused.

---

## 7-Gate Signal Engine

Every trade requires passing a confidence score ≥ 70/100:

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

## Upgrade History

| Upgrade | Feature                                                  | Status |
| ------- | --------------------------------------------------------- | ------ |
| A       | LSTM 3-layer neural network (60h sequence)               | ✅     |
| B       | Backtesting with vectorbt (1yr ETH+BTC)                  | ✅     |
| C       | Paper trading on Binance Testnet                         | ✅     |
| D       | PPO Reinforcement Learning Agent (200k steps)            | ✅     |
| E       | KATANA Dashboard (Streamlit, Crimson theme)              | ✅     |
| F       | Short selling + ATR stop-loss + trailing stop            | ✅     |
| G       | Telegram alerts + 5-coin expansion                       | ✅     |
| H       | Full backtest all 5 coins (real results)                 | ✅     |
| I       | Phase 2 honest retraining — fixed Sharpe evaluation bug  | ✅     |

---

## Earlier Backtest (Upgrade H — vectorbt, separate pipeline)

| Coin    | Return     | Trades | Win Rate | Max Drawdown |
| ------- | ---------- | ------ | -------- | ------------- |
| ETH     | -15.3%     | 65     | 58.5%    | -45.3%        |
| BTC     | -14.1%     | 70     | 54.3%    | -39.8%        |
| SOL     | -12.0%     | 78     | 62.8%    | -46.5%        |
| **BNB** | **+16.9%** | 71     | 64.8%    | -31.2%        |
| ADA     | -61.2%     | 75     | 53.3%    | -69.0%        |

> This backtest uses a different evaluation pipeline (`backtest_runner.py` / vectorbt) than the RL Agent table above, run in an earlier phase, and has not been re-audited alongside the Phase 2 Sharpe fix. Treat these figures independently from the "Key Results" section above rather than as directly comparable.

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

### Option 1 — Hugging Face (no setup needed)

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

Create a `.env` file (never commit this):

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
| Exchange   | Binance Testnet (paper money only)               |

---

## Disclaimer

> This is a **paper trading** project built for learning purposes. No real money is used or at risk. Past backtest performance does not guarantee future results. Crypto trading carries significant risk.

---

**Builder:** Shivam (ZORO) · **Status:** Phase 4 Complete (Phase 2 honest retraining applied) · **Exchange:** Binance Testnet only
