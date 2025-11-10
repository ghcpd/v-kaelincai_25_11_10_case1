#!/bin/bash
set -e
if [ ! -d ".venv" ]; then
  echo "Please run setup.sh first to create virtual env and install dependencies.";
  exit 1
fi
source .venv/bin/activate
mkdir -p results logs
rm -f logs/log_post.txt logs/trace_post.json
python -m pytest -q --color=yes tests/ --maxfail=1 --disable-warnings || true
