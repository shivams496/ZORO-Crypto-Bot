#!/bin/bash
# start.sh — runs FastAPI + trader in background, Streamlit dashboard in foreground
set -e
echo "[START] Launching ZORO Phase 4..."

# FastAPI — internal only, dashboard.py talks to it via localhost:8000
uvicorn api:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "[START] FastAPI running (PID $API_PID) on :8000 (internal)"
sleep 2

# Trading loop — background, keeps writing to DB / trade log continuously
python -X faulthandler trader.py &
TRADER_PID=$!
echo "[START] trader.py running (PID $TRADER_PID)"

# Streamlit dashboard — FOREGROUND, on :7860 (the port Hugging Face routes to)
echo "[START] Launching Streamlit dashboard on :7860 (public)"
streamlit run dashboard.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true

# Clean up background processes if Streamlit exits
kill $API_PID $TRADER_PID 2>/dev/null || true