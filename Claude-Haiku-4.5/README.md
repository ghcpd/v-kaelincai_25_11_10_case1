# AI Model Evaluation: Search History Dropdown Feature

## Overview

This evaluation framework tests an AI model's ability to design, implement, and validate a **Search History Dropdown** feature for an application. The framework compares a baseline application (Project A) with no history features against an enhanced version (Project B) that includes keyboard navigation, persistence, and privacy controls.

**Goal:** Provide quantitative metrics on feature correctness, UX quality (keyboard navigation), robustness (XSS prevention), persistence, and readiness for production rollout.

---

## Project Structure

```
c:\chatWorkspace\
├── README.md                          # This file
├── run_all.sh                         # Master test runner (runs both projects)
├── compare_report.md                  # Generated comparison report
│
├── Project_A_Baseline_Search/         # Pre-Feature (Baseline)
│   ├── requirements.txt               # Python dependencies
│   ├── setup.sh                       # Environment setup
│   ├── run_tests.sh                   # Test runner
│   │
│   ├── src/
│   │   ├── index.html                 # Simple search UI (no dropdown)
│   │   └── app.js                     # Enter-only search implementation
│   │
│   ├── server/
│   │   └── server.py                  # Flask development server
│   │
│   ├── tests/
│   │   └── test_pre_feature.py        # Baseline tests
│   │
│   ├── logs/
│   │   └── *.txt                      # Server/execution logs
│   │
│   └── results/
│       └── results_pre.json           # Test results JSON
│
├── Project_B_SearchHistory/           # Post-Feature (Enhanced)
│   ├── requirements.txt               # Python dependencies
│   ├── setup.sh                       # Environment setup
│   ├── run_tests.sh                   # Test runner
│   │
│   ├── src/
│   │   ├── index.html                 # Enhanced search UI with dropdown
│   │   └── search_history.js          # History dropdown + persistence logic
│   │
│   ├── server/
│   │   └── server.py                  # Flask development server
│   │
│   ├── tests/
│   │   └── test_post_feature.py       # Enhanced feature tests
│   │
│   ├── logs/
│   │   └── *.txt                      # Server/execution logs
│   │
│   └── results/
│       └── results_post.json          # Test results JSON
│
└── shared_artifacts/                  # Shared test data and aggregated results
    ├── test_data.json                 # 10 comprehensive test cases
    └── results/
        ├── results_pre.json           # Copied from Project A
        ├── results_post.json          # Copied from Project B
        └── aggregated_metrics.json    # Combined metrics
```

---

## Quick Start

### 1. Run All Tests (One Command)

```bash
cd c:\chatWorkspace
bash run_all.sh
```

This single command will:
- ✓ Set up both project environments
- ✓ Start servers for each project
- ✓ Run comprehensive test suites
- ✓ Collect performance metrics
- ✓ Generate comparison report: `compare_report.md`
- ✓ Save results: `shared_artifacts/results/`

**Expected output:**
- Exit code 0: All tests passed
- Exit code >0: Some tests failed (see logs for details)

### 2. Run Individual Projects

**Project A (Baseline - Enter-only search):**
```bash
cd c:\chatWorkspace\Project_A_Baseline_Search
bash run_tests.sh
```

**Project B (Enhanced - Search History Dropdown):**
```bash
cd c:\chatWorkspace\Project_B_SearchHistory
bash run_tests.sh
```

---

## Test Data

### Test Cases (in `shared_artifacts/test_data.json`)

| Test ID | Category | Description |
|---------|----------|-------------|
| TC_001 | Normal | Empty history - no dropdown shown |
| TC_002 | Normal | History display on focus - most recent first |
| TC_003 | Normal | New search added to history |
| TC_004 | Repeated | Duplicate searches - deduplication/reordering |
| TC_005 | Keyboard | Arrow keys and Enter for navigation |
| TC_006 | Interaction | Click history item to repeat search |
| TC_007 | Persistence | History survives page reload |
| TC_008 | Privacy | Clear history button functionality |
| TC_009 | Robustness | XSS prevention - malformed input sanitized |
| TC_010 | Privacy | Opt-out disables persistence |

### Input/Output Format

Each test case includes:
- **Initial State:** Pre-populated history, persistence settings
- **User Actions:** Sequences of focus, type, click, keyboard navigation
- **Expected Output:** Dropdown visibility, item list, search payload, storage state
- **Acceptance Criteria:** Boolean assertions for pass/fail determination

**Example (TC_002):**
```json
{
  "id": "TC_002_normal_history_display",
  "initial_state": {
    "history": ["python tutorial", "javascript async", "css grid layout"],
    "persistence_enabled": true,
    "opt_out": false
  },
  "user_actions": [
    { "action": "focus", "target": "search_input" }
  ],
  "expected_output": {
    "dropdown_visible": true,
    "dropdown_items": ["css grid layout", "javascript async", "python tutorial"],
    "items_count": 5,
    "search_triggered": false
  }
}
```

---

## Features Tested

### Project A (Baseline)
- ✓ Enter key triggers search
- ✓ Search result display
- ✓ Empty input rejection

### Project B (Enhanced)
All Project A features, plus:
- ✓ **History Dropdown:** 5 most recent searches shown on focus/typing
- ✓ **Keyboard Navigation:** 
  - `↑` / `↓` arrows to navigate items
  - `Enter` to select highlighted item
  - `Esc` to close dropdown
- ✓ **Click to Repeat:** Click history item triggers same search
- ✓ **Persistence:** localStorage saves history across page reloads
- ✓ **Privacy Controls:**
  - Clear history button
  - Opt-out toggle (disables persistence, clears history)
- ✓ **Security:** XSS prevention via HTML entity encoding
- ✓ **Accessibility:** ARIA attributes (role, aria-expanded, etc.)

---

## Execution & Artifacts

### Test Execution Flow

1. **Setup Phase**
   - Create Python venv
   - Install dependencies (Flask, Playwright, pytest, aiohttp)
   - Install Playwright browsers

2. **Server Start**
   - Flask dev server starts on `http://localhost:PORT`
   - Health check waits for server readiness

3. **Browser Tests** (Playwright/headless)
   - Navigate to app
   - Simulate user interactions (focus, type, click, keyboard)
   - Capture DOM state, search payloads, localStorage contents
   - Measure latencies

4. **Result Collection**
   - Per-test: pass/fail, assertions, details
   - Metrics: correctness %, keyboard nav success, persistence success, latency

5. **Report Generation**
   - Aggregate metrics from both projects
   - Calculate deltas (improvement %)
   - Generate markdown comparison report

### Output Artifacts

**Per-Project:**
- `logs/server.log` — Server startup and request logs
- `logs/log_pre.json` / `log_post.json` — Test execution logs
- `results/results_pre.json` / `results_post.json` — Detailed test results

**Shared:**
- `shared_artifacts/results/aggregated_metrics.json` — Combined metrics
- `compare_report.md` — Human-readable comparison report

**Example `results_pre.json`:**
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
      "details": { "dropdown_visible": false },
      "timestamp": "2025-11-10T14:23:46.234567"
    }
  ]
}
```

---

## Metrics & Evaluation Criteria

### Quantitative Metrics

| Metric | Project A (Baseline) | Project B (Enhanced) | Target |
|--------|----------------------|----------------------|--------|
| **Correctness Rate** | 100% | ≥95% | ≥95% |
| **Test Coverage** | 6 tests | 10 tests | ≥10 |
| **Keyboard Nav Success** | N/A | ≥8/10 | ≥80% |
| **Persistence Success** | N/A | ≥1/10 | 100% |
| **Dropdown Latency** | N/A | <300ms | <500ms |

### Acceptance Criteria

**Project B must satisfy ALL:**
1. ✓ Dropdown shows on focus/typing with ≤5 most recent items
2. ✓ Items displayed in most-recent-first order (after deduplication)
3. ✓ Click or keyboard selection triggers same search request
4. ✓ History persists across page reloads (localStorage)
5. ✓ Clear history button works (removes all entries)
6. ✓ Opt-out toggle disables persistence and clears history
7. ✓ Keyboard navigation (↑↓Enter/Esc) works reliably
8. ✓ XSS prevention: malformed inputs sanitized (no script execution)
9. ✓ ARIA attributes accessible for screen readers
10. ✓ No regressions in Project A baseline functionality

---

## Configuration & Customization

### Environment Variables

```bash
# Project A
export PORT=5001              # Server port (default 5000)
export HEADLESS=1             # Playwright headless mode (default 1)

# Project B
export PORT=5002
export MAX_HISTORY_SIZE=50    # Max items stored (default 50)
export MAX_RECENT_SHOWN=5     # Max items in dropdown (default 5)
```

### Storage Backends

**Default:** browser `localStorage`
- Persists across page reloads within same origin
- ~5-10MB quota (browser-dependent)
- No server-side persistence

**Alternative (optional):** Modify `search_history.js` to support:
- IndexedDB (larger quota, more reliable)
- Server-side session storage
- Cloud sync (Firebase, AWS Amplify)

### Privacy Settings

**In Project B HTML:**
```html
<!-- Users can opt-out of history tracking -->
<input id="opt_out_toggle" type="checkbox" />
<label>Disable History</label>
```

When toggled:
- `localStorage` cleared immediately
- New searches not saved
- Opt-out preference persisted separately

---

## Known Limitations & Pitfalls

### Test Harness Limitations

1. **Headless vs Real Device**
   - Tests run in headless Chromium (no GPU, limited touch)
   - Recommend real-device testing before rollout
   - Mobile keyboard/touch interactions may differ

2. **Race Conditions**
   - Rapid repeated searches may conflict on storage writes
   - Mitigation: Debounce input, implement optimistic locking

3. **Storage Quota Errors**
   - localStorage quota exceeded if history too large
   - Mitigation: Implement quota checking, cleanup old entries

4. **Cross-Origin Issues**
   - localStorage is same-origin only
   - Subdomain history sharing requires shared domain or service worker

5. **Concurrent Writes**
   - Multiple tabs writing history simultaneously may lose data
   - Mitigation: Use StorageEvent listener to sync across tabs

### Feature Implementation Challenges

1. **Keyboard Navigation**
   - Different browsers handle arrow key focus differently
   - Screen reader announcements need manual ARIA management

2. **Persistence Reliability**
   - Private/Incognito mode may block localStorage
   - Fallback to memory-only history needed

3. **XSS Prevention**
   - textContent escaping sufficient for this simple feature
   - Complex scenarios (nested HTML) require sanitization library (DOMPurify)

4. **Performance at Scale**
   - 1000+ items in history: DOM rendering slow
   - Mitigation: Virtualize dropdown, implement pagination

5. **Privacy Expectations**
   - Users may expect encrypted or deleted history
   - Recommend clear privacy policy documentation

---

## Monitoring & Rollout Strategy

### Recommended Rollout Phases

**Phase 1: Pilot (1 week, 5-10% traffic)**
- Monitor: dropout rate, JS errors, storage quota exceeded
- Rollback trigger: >0.5% error rate
- Metrics: User engagement with dropdown, search conversion impact

**Phase 2: Ramped (1-2 weeks, 50% traffic)**
- Monitor: same as Phase 1 + persistence success, keyboard nav usage
- Rollback trigger: >1% error rate or >5% regression in search completion
- Metrics: Abandoned searches with dropdown open, privacy opt-out rate

**Phase 3: Full Rollout (100% traffic)**
- Ongoing monitoring via analytics dashboard
- Alert on: storage quota exceeded, keyboard nav failures, opt-out >20%

### Telemetry Events

Recommended events to log in production:

```javascript
// Search History Dropdown Events
analytics.track('dropdown_opened', {
  trigger: 'focus|typing|keyboard',
  history_count: num_items,
  timestamp: Date.now()
});

analytics.track('dropdown_selection', {
  method: 'click|keyboard',
  item_age_ms: Date.now() - item.timestamp,
  position_in_list: index
});

analytics.track('history_cleared', {
  count: num_items_cleared,
  method: 'clear_button|opt_out',
  timestamp: Date.now()
});

analytics.track('storage_error', {
  error: error_message,
  attempt: 'persist|load|clear',
  timestamp: Date.now()
});
```

---

## Troubleshooting

### Tests Fail with "Server did not start"

**Solution:**
- Check port availability: `netstat -ano | findstr :5001` (Windows)
- Ensure no other services running on ports 5001-5002
- Increase server startup timeout in `test_*.py`

### "localStorage is not defined" error

**Solution:**
- Ensure tests run in Playwright with headless=true
- Check that `clear_storage()` is called before each test
- Some tests may need `wait_for_timeout()` for async storage writes

### Dropdown not appearing in tests

**Solution:**
- Verify CSS selector matches: `#history_dropdown`
- Check that history items exist before focusing
- Add explicit wait: `await page.wait_for_selector('.history-item')`
- Ensure JavaScript not throwing console errors

### Persistence tests fail after reload

**Solution:**
- Clear all tabs of the application (new browser context each test)
- Verify localStorage is not in private/incognito mode
- Check browser DevTools > Application > Storage for manual verification

### XSS test shows script execution

**Solution:**
- Verify `textContent` assignment (not `innerHTML`)
- Check that list items use `.textContent` not `.innerHTML`
- Add Content Security Policy header to prevent inline scripts

---

## Dependencies

### Python Packages
- **Flask 2.3.3** — Web server
- **Playwright 1.40.0** — Browser automation
- **pytest 7.4.3** — Test framework
- **aiohttp 3.9.1** — Async HTTP client
- **json5** — JSON parsing utility

### Browser
- **Chromium (via Playwright)** — Headless browser for test automation

### System Requirements
- Python 3.7+
- 500MB disk space (Playwright browser binary)
- Network access to localhost:5001-5002

---

## Examples

### Running Specific Test Case

```bash
# Project B - Run only keyboard navigation test
cd Project_B_SearchHistory
python -m pytest tests/test_post_feature.py::EnhancedSearchTester::test_keyboard_navigation -v
```

### Manual Testing

1. Start Project B server:
   ```bash
   cd Project_B_SearchHistory
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   python server/server.py
   ```

2. Open browser: `http://localhost:5000`

3. Test scenarios:
   - Type a search → press Enter
   - Focus input → see dropdown
   - Navigate with arrow keys → select with Enter
   - Click dropdown item → search repeats
   - Reload page → history persists
   - Click "Disable History" → toggle persists
   - Click "Clear History" → all removed

### Viewing Results

```bash
# View Project A results
cat Project_A_Baseline_Search/results/results_pre.json | python -m json.tool

# View comparison report
cat compare_report.md

# View aggregated metrics
cat shared_artifacts/results/aggregated_metrics.json | python -m json.tool
```

---

## Support & Documentation

### File Locations

- **Test Data Schema:** `shared_artifacts/test_data.json`
- **Results Format:** `Project_B_SearchHistory/results/results_post.json`
- **Comparison Report:** `compare_report.md` (generated)
- **Logs:** `Project_A_Baseline_Search/logs/` and `Project_B_SearchHistory/logs/`

### Extending Tests

To add a new test in `Project_B_SearchHistory/tests/test_post_feature.py`:

```python
async def test_custom_scenario(self):
    """TC_XXX: Custom test description"""
    test_id = 'TC_XXX_custom'
    try:
        await self.clear_storage()
        await self.page.reload(wait_until='networkidle')
        
        # Test logic here
        
        self._record_test_pass(test_id, {
            'custom_assertion': True,
            'detail': 'value'
        })
    except AssertionError as e:
        self._record_test_fail(test_id, str(e))
```

Then add to `run_all_tests()`:
```python
await self.test_custom_scenario()
```

---

## FAQ

**Q: Why are there two projects?**  
A: Project A establishes a baseline for pre-feature behavior (search-only). Project B demonstrates the complete feature implementation. Comparison shows the delta in complexity and UX capability.

**Q: Can I run tests without Docker?**  
A: Yes! This evaluation uses local Python venvs and Playwright (lighter than Docker). Just run `setup.sh` in each project.

**Q: How long do tests take?**  
A: ~2-3 minutes per project (server startup + 10 test cases + browser automation overhead).

**Q: Is the history data encrypted?**  
A: No, localStorage is plain-text. For sensitive applications, use server-side storage or encrypt via libsodium.js.

**Q: Can history be shared across devices?**  
A: Not in this version. Extend by syncing via backend API and user authentication.

---

## License & Attribution

This evaluation framework is provided as-is for AI model testing and feature validation. Use for internal evaluation only.

---

**Generated:** 2025-11-10  
**Version:** 1.0  
**Evaluation Type:** AI Model — Feature & Improvement (New Feature)
