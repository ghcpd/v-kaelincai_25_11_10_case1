# Test Execution Guide & Examples

## Overview

This document provides concrete examples of how the test framework executes and what to expect.

## Test Execution Flow

### Phase 1: Setup (30 seconds)

```bash
$ bash run_all.sh

╔════════════════════════════════════════════════════════════╗
║          AI MODEL EVALUATION - FEATURE IMPLEMENTATION       ║
║     Search History Dropdown: Pre vs Post Feature Analysis   ║
╚════════════════════════════════════════════════════════════╝

Timestamp: Wed Nov 10 14:23:45 UTC 2025
Repository Root: /workspace/chatWorkspace

────────────────────────────────────────────────────────────
[1/2] Running PROJECT A - BASELINE tests...
────────────────────────────────────────────────────────────

[Setup] Creating Python virtual environment for Project A...
[Setup] Installing dependencies...
[Setup] Installing Playwright browsers...
[Setup] Setup complete! Virtual environment ready.
```

### Phase 2: Project A Tests (45 seconds)

```
============================================================
PROJECT A - BASELINE SEARCH TESTS
============================================================

Running baseline functionality tests...

✓ Server started on http://localhost:5001
✓ Navigated to http://localhost:5001

Running baseline functionality tests...

  ✓ TC_001_empty_history: PASS
  ✓ TC_002_enter_search: PASS
  ✓ TC_003_multiple_searches: PASS
  ✓ TC_004_other_keys_ignored: PASS
  ✓ TC_005_empty_input: PASS
  ✓ TC_006_special_chars: PASS

✓ Server stopped
✓ Results saved to /workspace/chatWorkspace/Project_A_Baseline_Search/results/results_pre.json

============================================================
TEST SUMMARY - PROJECT A (BASELINE)
============================================================
Total Tests:        6
Passed:             6
Failed:             0
Correctness Rate:   100.0%
============================================================

✓ PROJECT A - BASELINE tests completed successfully
```

### Phase 3: Project B Tests (60 seconds)

```
────────────────────────────────────────────────────────────
[2/2] Running PROJECT B - ENHANCED tests...
────────────────────────────────────────────────────────────

[Setup] Activating virtual environment...
[Setup] Python version: Python 3.9.13
[Setup] Pip packages: 42

[Test] Running enhanced search history tests...

============================================================
PROJECT B - ENHANCED SEARCH HISTORY TESTS
============================================================

Running enhanced search history tests...

✓ Server started on http://localhost:5002
✓ Navigated to http://localhost:5002

Running enhanced search history tests...

  ✓ TC_002_empty_history_focus: PASS
  ✓ TC_003_history_display_focus: PASS
  ✓ TC_006_click_repeat: PASS
  ✓ TC_005_keyboard_nav: PASS
  ✓ TC_005_esc_closes: PASS
  ✓ TC_007_persistence_reload: PASS
  ✓ TC_008_clear_history: PASS
  ✓ TC_010_opt_out: PASS
  ✓ TC_009_xss_prevention: PASS
  ✓ TC_003_max_5_items: PASS

✓ Server stopped
✓ Results saved to /workspace/chatWorkspace/Project_B_SearchHistory/results/results_post.json

============================================================
TEST SUMMARY - PROJECT B (ENHANCED)
============================================================
Total Tests:                10
Passed:                     9
Failed:                     1
Correctness Rate:           90.0%
Keyboard Navigation Success:8
Persistence Success:        1
Avg Dropdown Latency:       45.23ms
============================================================

✓ PROJECT B - ENHANCED tests completed successfully
```

### Phase 4: Aggregation & Reporting (10 seconds)

```
────────────────────────────────────────────────────────────
Aggregating results and generating comparison report...
────────────────────────────────────────────────────────────

✓ Loaded Project A results: 6 tests
✓ Loaded Project B results: 10 tests
✓ Saved aggregated metrics to /workspace/chatWorkspace/shared_artifacts/results/aggregated_metrics.json
✓ Comparison report generated: /workspace/chatWorkspace/compare_report.md

════════════════════════════════════════════════════════════
✓ EVALUATION COMPLETE
════════════════════════════════════════════════════════════

Generated Artifacts:
  • Comparison Report: /workspace/chatWorkspace/compare_report.md
  • Results Directory: /workspace/chatWorkspace/shared_artifacts/results/

$
```

## Test Output Examples

### Individual Test Execution (Project A)

```bash
$ cd Project_A_Baseline_Search
$ bash run_tests.sh

============================================================
PROJECT A - BASELINE SEARCH TEST RUNNER
============================================================

[Setup] Virtual environment not found. Creating...
[Setup] Activating virtual environment...
[Setup] Python version: Python 3.9.13
[Setup] Pip packages: 32

[Test] Running baseline search tests...

Running baseline functionality tests...

Test TC_001 (Empty History):
  - Focus on empty search input
  - Verify no dropdown elements present
  ✓ PASS

Test TC_002 (Enter Triggers Search):
  - Type "python tutorial"
  - Press Enter
  - Wait 300ms for result
  - Verify result displayed
  - Verify input cleared
  - Latency: 142ms
  ✓ PASS

Test TC_003 (Multiple Searches):
  - Perform 3 searches
  - Verify 3 results displayed
  - Reload page
  - Verify no results persisted (baseline)
  ✓ PASS

...

[Results] Test execution completed with exit code: 0
[Results] Results saved to: /workspace/chatWorkspace/Project_A_Baseline_Search/results/results_pre.json
[Results] Logs saved to: /workspace/chatWorkspace/Project_A_Baseline_Search/logs/

✓ All tests passed!
```

### Results JSON Output

**Project A Results (`results_pre.json`):**
```json
{
  "project": "Project_A_Baseline_Search",
  "timestamp": "2025-11-10T14:23:45.123456",
  "metrics": {
    "total_tests": 6,
    "passed_tests": 6,
    "failed_tests": 0,
    "correctness_rate": 100.0
  },
  "test_results": [
    {
      "test_id": "TC_001_empty_history",
      "status": "PASS",
      "details": {
        "dropdown_visible": false,
        "empty_history_handled": true
      },
      "timestamp": "2025-11-10T14:23:46.234567"
    },
    {
      "test_id": "TC_002_enter_triggers_search",
      "status": "PASS",
      "details": {
        "search_triggered": true,
        "result_displayed": true,
        "query_in_result": true,
        "input_cleared": true,
        "latency_ms": 142.5
      },
      "timestamp": "2025-11-10T14:23:50.567890"
    }
  ]
}
```

**Project B Results (`results_post.json`):**
```json
{
  "project": "Project_B_SearchHistory",
  "timestamp": "2025-11-10T14:24:15.123456",
  "metrics": {
    "total_tests": 10,
    "passed_tests": 9,
    "failed_tests": 1,
    "keyboard_nav_success": 8,
    "persistence_success": 1,
    "avg_dropdown_latency_ms": 45.23,
    "correctness_rate": 90.0
  },
  "test_results": [
    {
      "test_id": "TC_003_history_display_focus",
      "status": "PASS",
      "details": {
        "dropdown_visible": true,
        "items_count": 3,
        "correct_order": true,
        "latency_ms": 45.23
      },
      "timestamp": "2025-11-10T14:24:20.456789"
    },
    {
      "test_id": "TC_005_keyboard_nav",
      "status": "PASS",
      "details": {
        "arrow_down_navigates": true,
        "enter_selects": true,
        "search_triggered": true
      },
      "timestamp": "2025-11-10T14:24:25.789012"
    }
  ]
}
```

### Comparison Report Excerpt

The generated `compare_report.md` contains:

```markdown
# AI Model Evaluation Report
## Search History Dropdown Feature Implementation

**Evaluation Date:** 2025-11-10 14:24:45

## Executive Summary

This report evaluates the implementation of a Search History Dropdown feature...

## Test Results Comparison

| Metric | Project A (Baseline) | Project B (Enhanced) | Delta |
|--------|----------------------|----------------------|-------|
| Total Tests | 6 | 10 | +4 |
| Passed Tests | 6 | 9 | +3 |
| Failed Tests | 0 | 1 | +1 |
| Correctness Rate | 100.0% | 90.0% | -10.0% |

## Feature Coverage Analysis

### Project A (Baseline)
- ✓ Enter-only search trigger
- ✓ Search result display
- ✗ No history dropdown
- ✗ No keyboard navigation
- ✗ No persistence
- ✗ No privacy controls

### Project B (Enhanced)
- ✓ Enter-only search trigger
- ✓ Search result display
- ✓ History dropdown (5 most recent)
- ✓ Keyboard navigation (↑↓ Enter Esc)
- ✓ Click-to-repeat search
- ✓ Persistence across page reloads
- ✓ Privacy controls (clear history, opt-out)
- ✓ XSS prevention & sanitization

...

## Acceptance Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| Display 5 most recent searches | ✓ PASS | Test coverage includes max items limit |
| Show on focus/typing | ✓ PASS | Focus event handler tested |
| Click to repeat search | ✓ PASS | Mouse interaction tested |
| Keyboard navigation | ✓ PASS | Up/Down/Enter/Esc tested |
| Persist across reloads | ✓ PASS | localStorage persistence verified |
| Privacy controls | ✓ PASS | Clear history & opt-out tested |
| Robust input handling | ✓ PASS | XSS prevention tested |

...

## Conclusion

Project B successfully implements all required features for the Search History Dropdown:
- **Correctness Rate:** 90.0%
- **Test Coverage:** 9/10 tests passing
- **Performance:** Dropdown latency 45.23ms

The feature is recommended for production rollout with the suggested monitoring
and gradual deployment strategy outlined above.
```

## Expected Latency Measurements

### Typical Latencies Observed

```
Dropdown Display Latencies (Project B):
  On focus (empty history):        2-5ms
  On focus (5 items):              20-50ms
  On typing (filter):              5-30ms
  After keyboard navigation:       10-20ms

Search Execution Latencies:
  After Enter key:                 50-200ms
  After keyboard selection:        50-200ms
  After click selection:           50-200ms

Persistence Latencies:
  Save to localStorage:            1-5ms
  Restore from localStorage:       2-10ms
  Page reload (full):              500-2000ms

Overall Test Execution:
  Project A (6 tests):             30-60 seconds
  Project B (10 tests):            40-80 seconds
  Full run (both projects):        2-5 minutes
```

## Failure Scenarios

### Example: Server Startup Failure

```
✗ ERROR: Server startup timeout

[2025-11-10 14:23:45] Starting Project A server on port 5001
[2025-11-10 14:23:46] Waiting for server health check...
[2025-11-10 14:23:47] Retry 1/30...
[2025-11-10 14:23:48] Retry 2/30...
...
[2025-11-10 14:23:60] Retry 15/30...
[ERROR] Server did not start within 15.0 seconds

Possible causes:
- Port 5001 already in use
- Flask import error
- Missing dependencies

Solution:
- Run: netstat -ano | findstr :5001
- Kill existing process or change PORT
- Verify requirements.txt installed
```

### Example: Test Failure

```
✗ TC_007_persistence_reload: FAIL

Expected: History restored after reload
Actual: localStorage returns empty array

Debug Info:
  - Before reload: {"history": [{"query": "test"}]}
  - After reload: {"history": []}
  - Page reloaded: true
  - Storage key: search_history_data
  - Browser: Chromium (headless)

Root cause analysis:
- Check if Playwright clearing storage between tests
- Verify clear_storage() not called in test
- Check localStorage quota not exceeded
```

## Manual Verification Commands

```bash
# Check if tests were created correctly
find . -name "test_*.py" -exec wc -l {} \;

# Validate Python syntax
python -m py_compile Project_A_Baseline_Search/tests/test_pre_feature.py

# Check JSON validity
python -c "import json; json.load(open('shared_artifacts/test_data.json'))"

# View specific test case
python -c "import json; data = json.load(open('shared_artifacts/test_data.json')); print(json.dumps(data['test_cases'][0], indent=2))"

# Check server startup
python Project_A_Baseline_Search/server/server.py &
sleep 2
curl http://localhost:5000/api/health
```

---

**This document shows realistic test output and helps understand what to expect during execution.**
