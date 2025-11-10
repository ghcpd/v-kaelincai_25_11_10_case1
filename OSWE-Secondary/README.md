# Search History Dropdown Evaluation

This repository contains two projects for testing a Search History Dropdown feature: Project_A_Baseline_Search and Project_B_SearchHistory.

Setup (project-level):

- Use bash or PowerShell. On Windows run setup in PowerShell: `./setup.sh` will create venv and install dependencies.

How to run tests:

- Project A:
  - cd Project_A_Baseline_Search
  - ./setup.sh
  - pytest

- Project B:
  - cd Project_B_SearchHistory
  - ./setup.sh
  - pytest

- Full run (both projects):
  - ./run_all.sh
  - On Windows PowerShell also available: run `./Project_A_Baseline_Search/run_tests.ps1` then `./Project_B_SearchHistory/run_tests.ps1` and then `python compare_report.py`.

Notes:
- Search requests are logged to `Project_A_Baseline_Search/logs/log_pre.txt` and `Project_B_SearchHistory/logs/log_post.txt`.
- Collected test artifacts are in each project's `results/` directory and aggregated results appear in `results/aggregated_metrics.json` after `run_all.sh`.

Persistence options:
- By default the search history is stored in the browser localStorage under the key `search_history`.
- To emulate in-memory persistence (no file), use the opt-out checkbox in `Project_B_SearchHistory` which stops writing to localStorage.
- For server-side persistence or cross-client syncing, swap the storage API to POST entries to a backend and update the test harness accordingly.

Artifacts:
- results_pre.json and results_post.json are written to each project after tests.
- Aggregated metrics are in `results/aggregated_metrics.json` after `run_all.sh`.
- `compare_report.md` has a textual comparison summary.

Limitations:
- Headless browsers differ from real devices: keyboard event order and focus management may slightly differ.

Rollout suggestion:
- Manage via a feature flag. Monitor search usage and top keywords stored.
