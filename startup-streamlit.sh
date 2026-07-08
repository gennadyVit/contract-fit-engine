#!/bin/bash
VENV_BIN=$(python -c "import sys; print(sys.prefix)")/bin
$VENV_BIN/streamlit run streamlit/app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true
