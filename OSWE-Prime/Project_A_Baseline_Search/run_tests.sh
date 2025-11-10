#!/bin/bash
set -e
ROOT=$(pwd)
if [ ! -d ".venv" ]; then
  echo "Please run setup.sh first to create virtual env and install dependencies.";
  exit 1
fi
source .venv/bin/activate
mkdir -p results logs
rm -f logs/log_pre.txt logs/trace_pre.json
python -m pytest -q --color=yes tests/ --maxfail=1 --disable-warnings || true
