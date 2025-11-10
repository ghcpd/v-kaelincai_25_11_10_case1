# Search History Dropdown - Experiment

This workspace contains two independent demo projects to evaluate the addition of a Search History Dropdown feature.

Project A - Baseline: Enter-only search bar (no history dropdown)
Project B - Enhanced: Search bar with history dropdown, keyboard nav, persistence and privacy controls

Use `run_all.sh` from the repo root to execute tests for both projects in sequence and generate aggregated results and a report.

Requirements:
- Bash or a POSIX shell for `run_all.sh`.
- Python 3.8+, `venv` and pip. Each project's setup.sh will create per-project venvs and install dependencies, including Playwright and its browser binaries.

On Windows PowerShell, run the included PowerShell scripts if available or run via WSL/Git Bash. See per-project README for details.
