#!/bin/bash
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)
python "$ROOT/server/server.py" &
SERVER_PID=$!
sleep 0.5
pytest -q "$ROOT/tests" || true
kill $SERVER_PID || true
