#!/bin/bash

# Project B - Search History Setup

set -e

echo "[Setup] Creating Python virtual environment for Project B..."
python -m venv venv

# Activate venv based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "[Setup] Installing dependencies..."
pip install --upgrade pip setuptools
pip install -r requirements.txt

echo "[Setup] Installing Playwright browsers..."
playwright install chromium

echo "[Setup] Setup complete! Virtual environment ready."
echo "[Setup] To activate: source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)"
