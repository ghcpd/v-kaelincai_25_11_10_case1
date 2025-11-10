#!/bin/bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install
echo "Setup complete. Activate venv with: source .venv/bin/activate"
