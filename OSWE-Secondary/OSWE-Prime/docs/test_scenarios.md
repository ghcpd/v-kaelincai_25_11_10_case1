Test scenarios and descriptions used by both projects:

1. Show/Use 5 most recent searches:
- When the search input is focused or typed into, the dropdown shows up to 5 most recent searches, most-recent-first.
- Click on history item triggers same search as typing and pressing Enter.
- Keyboard Up/Down arrow highlights items and Enter selects.
- Escape hides dropdown.

2. Deduplication & ordering:
- Repeated search moves the item to front.
- Duplicates are removed, only one entry kept.

3. Malformed inputs:
- If history contains values that are not strings (null, numbers) they are ignored.
- Very long strings are accepted but may be truncated by UI.

4. Persistence & Opt-out:
- By default, search history is saved to localStorage and persists across reloads.
- Checking the opt-out checkbox prevents saving new searches.

Acceptance criteria:
- Dropdown appears on focus/typing.
- Show up to 5 most recent entries; most-recent-first.
- Clicking or selecting item triggers same network request payload.
- History persists when not opted-out.
- Clear history button removes items and storage entry.

Test input/output format for automated tests:
- JSON test vector with keys: id, initial_state, actions, expected
- Example action: {"action":"focus"}
- Example expected: {"dropdown": true, "items": ["x","y","z"]}

Pitfalls and failure modes:
- Concurrent writes: multiple tabs saving history at once could lead to ordering races; consider using a server-side write serialization or a compare-and-set approach.
- Large history: storing too many items in localStorage can hit quota limits; keep a cap (we store up to 100) and show only 5 in the UI.
- Malicious entries: untrusted content could contain control characters; sanitize the UI rendering and limit length to avoid layout issues.
- Cross-origin storage: localStorage is bound to origin; keep tests in same host.
