#!/usr/bin/env bash
# Run baseline tests; optional repeat count
if [ -d .venv ]; then
  . .venv/bin/activate
fi
COUNT=${1:-1}
for i in $(seq 1 $COUNT); do
  echo "Run $i/$COUNT"
  pytest -q || true
done
