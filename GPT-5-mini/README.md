# Search History Dropdown Evaluation

This workspace contains two projects for evaluating a Search History Dropdown feature:

- Project_A_Baseline_Search: Enter-only search bar (pre-feature)
- Project_B_SearchHistory: Enhanced search with dropdown, keyboard navigation, persistence, privacy controls

How to run (one command):

1. On a system with bash (Git Bash / WSL / MSYS), run: bash run_all.sh

This will start each project's server, run tests, and produce artifacts under `results/`.

Limitations:
- The scripts assume a bash environment for orchestration. On Windows PowerShell, run individual project `run_tests.sh` with Bash or run pytest manually.
- Playwright may require additional dependencies on Windows; see Playwright docs.

Rollout suggestions:
- Feature flag the dropdown, monitor telemetry for search selection vs typed searches, gradually enable for small percent of users.
