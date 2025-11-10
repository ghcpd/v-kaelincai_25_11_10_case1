(() => {
  const input = document.getElementById('search');
  const historyEl = document.getElementById('history');
  const results = document.getElementById('results');
  const clearBtn = document.getElementById('clear');
  const optout = document.getElementById('optout');

  const STORAGE_KEY = 'search_history_v1';
  const MAX_ITEMS = 100; // we'll display up to 5 but keep more for usefulness
  const DISPLAY = 5;

  function readStorage() {
    try {
      if (optout.checked) return [];
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const arr = JSON.parse(raw);
      if (!Array.isArray(arr)) return [];
      return arr.filter(x => typeof x === 'string');
    } catch (e) {
      console.error('storage-read', e);
      return [];
    }
  }

  function writeStorage(arr) {
    try {
      if (optout.checked) return;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(arr.slice(0, MAX_ITEMS)));
    } catch (e) { console.error('storage-write', e); }
  }

  function addHistory(item) {
    if (typeof item !== 'string') return;
    let arr = readStorage();
    // dedupe: remove existing and unshift
    arr = arr.filter(x => x !== item);
    arr.unshift(item);
    writeStorage(arr);
  }

  function buildDropdown(filter) {
    const arr = readStorage();
    let items = arr;
    if (filter) items = items.filter(s => s.toLowerCase().includes(filter.toLowerCase()));
    items = items.slice(0, DISPLAY);
    historyEl.innerHTML = '';
    items.forEach((s, i) => {
      const d = document.createElement('div');
      d.className = 'history-item';
      d.setAttribute('role', 'option');
      d.setAttribute('data-index', i);
      d.textContent = s;
      d.addEventListener('mousedown', (ev) => {
        // mousedown to avoid losing focus before click
        ev.preventDefault();
        selectItem(i);
      });
      historyEl.appendChild(d);
    });
    if (items.length) {
      historyEl.setAttribute('aria-hidden', 'false');
      input.setAttribute('aria-expanded', 'true');
      historyEl.style.display = 'block';
    } else {
      historyEl.setAttribute('aria-hidden', 'true');
      input.setAttribute('aria-expanded', 'false');
      historyEl.style.display = 'none';
    }
  }

  function closeDropdown() {
    historyEl.setAttribute('aria-hidden', 'true');
    input.setAttribute('aria-expanded', 'false');
    historyEl.style.display = 'none';
    focusedIndex = -1;
    updateHighlight();
  }

  function openDropdown() { buildDropdown(input.value); }

  let focusedIndex = -1;

  function updateHighlight() {
    const items = historyEl.querySelectorAll('.history-item');
    items.forEach((it, i) => {
      if (i === focusedIndex) {
        it.classList.add('focused');
        it.setAttribute('aria-selected', 'true');
      } else {
        it.classList.remove('focused');
        it.setAttribute('aria-selected', 'false');
      }
    });
  }

  function selectItem(index) {
    const items = historyEl.querySelectorAll('.history-item');
    if (index < 0 || index >= items.length) return;
    const value = items[index].textContent;
    input.value = value;
    sendSearch(value);
    addHistory(value);
    closeDropdown();
  }

  function sendSearch(query) {
    const payload = { query, timestamp: Date.now() };
    window.__LAST_SEARCH = payload;
    console.log('search-request', JSON.stringify(payload));
    results.textContent = 'Search sent: ' + query;
  }

  input.addEventListener('focus', () => { openDropdown(); });
  input.addEventListener('input', () => { buildDropdown(input.value); });
  input.addEventListener('keydown', (e) => {
    const items = historyEl.querySelectorAll('.history-item');
    if (e.key === 'ArrowDown') {
      if (items.length) { focusedIndex = Math.min(focusedIndex + 1, items.length - 1); updateHighlight(); }
      else { openDropdown(); }
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      if (items.length) { focusedIndex = Math.max(focusedIndex - 1, 0); updateHighlight(); }
      e.preventDefault();
    } else if (e.key === 'Enter') {
      if (focusedIndex >= 0) { selectItem(focusedIndex); }
      else { sendSearch(input.value); addHistory(input.value); }
      e.preventDefault();
    } else if (e.key === 'Escape') {
      closeDropdown();
      e.preventDefault();
    }
  });

  clearBtn.addEventListener('click', () => { writeStorage([]); buildDropdown(); });
  optout.addEventListener('change', () => { if (optout.checked) { localStorage.removeItem(STORAGE_KEY); buildDropdown(); } else { buildDropdown(); } });

  // Initialize UI
  buildDropdown();

  // Expose for tests
  window.__SEARCH_HISTORY = { readStorage, writeStorage, addHistory, STORAGE_KEY };
})();
