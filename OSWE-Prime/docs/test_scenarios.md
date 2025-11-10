Test Scenarios and Expected Inputs/Outputs

Each test case in `shared_test_data.json` contains:
- id: unique case ID
- description: short explanation
- initial_state: { history: [...] } - sets localStorage 'search_history_v1'
- actions: list of steps
- expected: expected state after actions: dropdown_present (bool), items (list), selected, persisted

Example action object (JSON):
{"action": "type", "value": "apple"}
{"action": "enter"}
{"action": "focus"}
{"action": "key", "value": "ArrowDown"}
{"action": "toggle_persistence", "value": false}
{"action": "reload"}

Acceptance criteria used by tests:
- Baseline: no dropdown on focus/typing; search requests only on Enter
- Enhanced: dropdown shows up to 5 most recent entries in MRU order; click/Enter selects and sends same payload; keyboard nav works; persistence and privacy controls operate as described
