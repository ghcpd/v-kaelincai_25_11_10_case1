# Project B - Search History Dropdown (Post-Feature)

This project demonstrates an enhanced search bar with a 5-item Search History Dropdown, keyboard navigation, persistence and privacy controls.

Acceptance criteria implemented by this demo:
- Shows up to 5 most recent searches in MRU order when input is focused or the user types
- Click of an item triggers the exact same search request to /search
- Keyboard navigation: ArrowUp/ArrowDown toggles highlight, Enter selects highlighted item, Esc closes dropdown
- Persistence across reloads via localStorage when Persist is checked
- Clear History button clears both storage and in-memory session history
- Opt-out via checkbox disables localStorage persistence (session history only)

How to run:
- `./setup.sh` (on POSIX) to create virtualenv and install dependencies
- `./run_tests.sh` to execute the test suite

