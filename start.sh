#!/usr/bin/env bash
set -e
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
