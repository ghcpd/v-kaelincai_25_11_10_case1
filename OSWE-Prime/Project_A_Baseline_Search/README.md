# Project A - Baseline Search (Pre-Feature)

This project demonstrates a simple search bar that triggers a search request on Enter only; no history dropdown is provided.

Acceptance criteria for baseline (used as control in A/B tests):
- No history dropdown displayed on focus or typing
- Search requests are only triggered on Enter key

How to run:
- `./setup.sh` creates a virtualenv and installs dependencies including Playwright browsers
- `./run_tests.sh` runs the Playwright-based test suite

Folder structure:
- src/: static website
- server/: Flask server serving the page and handling /search
- tests/: pytest+Playwright tests

Artifacts:
- logs/: server request logs
- results/: test run results
