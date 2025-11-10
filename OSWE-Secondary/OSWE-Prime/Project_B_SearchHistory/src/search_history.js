const input = document.getElementById('searchInput');
const dropdown = document.getElementById('historyDropdown');
const results = document.getElementById('results');
const clearBtn = document.getElementById('clearHistory');
const optCheckbox = document.getElementById('optOut');
const STORAGE_KEY = 'search_history';
const OPT_KEY = 'search_history_opt_out';
let inMemoryHistory = [];
let activeIndex = -1;
let displayedItems = [];

function loadOptOut() { return window.localStorage.getItem(OPT_KEY) === '1'; }
function setOptOut(v) { window.localStorage.setItem(OPT_KEY, v ? '1' : '0'); }

function loadHistory() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(x => typeof x === 'string');
  } catch (e) { return [] }
}

function saveHistory(arr) {
  if (loadOptOut()) return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
  } catch (e) {
    console.warn('Could not save history', e);
  }
}

function addToHistory(item) {
  if (typeof item !== 'string' || !item.trim()) return;
  const arr = loadHistory();
  // dedupe
  const filtered = arr.filter(x => x !== item);
  filtered.unshift(item);
  // keep max 100
  const trimmed = filtered.slice(0, 100);
  saveHistory(trimmed);
}

function showDropdown(filtered) {
  dropdown.innerHTML = '';
  if (!filtered || filtered.length === 0) { dropdown.hidden = true; return; }
  filtered.forEach((text, idx) => {
    const d = document.createElement('div');
    d.textContent = text;
    d.className = 'dropdown-item';
    d.id = 'history-item-' + idx;
    d.setAttribute('role', 'option');
    d.addEventListener('click', async () => {
      await triggerSearch(text);
    });
    dropdown.appendChild(d);
  });
  dropdown.hidden = false;
  displayedItems = filtered;
  activeIndex = -1;
}

function filterHistory(prefix) {
  const all = inMemoryHistory;
  if (!prefix) return all.slice(0,5);
  const p = prefix.toLowerCase();
  return all.filter(x => x.toLowerCase().includes(p)).slice(0,5);
}

async function triggerSearch(q) {
  if (!q) return;
  results.textContent = 'Searching: ' + q;
  const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
  const body = await res.json();
  results.textContent = 'Search results: ' + JSON.stringify(body);
  // add to history
  addToHistory(q);
  // reload memory
  inMemoryHistory = loadHistory();
}

input.addEventListener('focus', (e) => {
  inMemoryHistory = loadHistory();
  showDropdown(inMemoryHistory.slice(0,5));
});

input.addEventListener('input', (e) => {
  inMemoryHistory = loadHistory();
  showDropdown(filterHistory(input.value));
});

input.addEventListener('keydown', (e) => {
  if (dropdown.hidden) return;
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    activeIndex = Math.min(activeIndex + 1, displayedItems.length - 1);
    updateActive();
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeIndex = Math.max(activeIndex - 1, 0);
    updateActive();
  } else if (e.key === 'Enter') {
    if (activeIndex >= 0) {
      e.preventDefault();
      triggerSearch(displayedItems[activeIndex]);
      dropdown.hidden = true;
    } else {
      triggerSearch(input.value);
      dropdown.hidden = true;
    }
  } else if (e.key === 'Escape') {
    dropdown.hidden = true;
  }
});

function updateActive(){
  const items = Array.from(dropdown.querySelectorAll('.dropdown-item'));
  items.forEach((it, i) => {
    if (i === activeIndex) { it.classList.add('active'); it.setAttribute('aria-selected', 'true'); }
    else { it.classList.remove('active'); it.setAttribute('aria-selected', 'false'); }
  });
}

clearBtn.addEventListener('click', () => {
  try { window.localStorage.removeItem(STORAGE_KEY); } catch(e){}
  inMemoryHistory = [];
  showDropdown([]);
});

optCheckbox.addEventListener('change', (ev) => {
  setOptOut(ev.target.checked);
});

window.addEventListener('load', () => {
  optCheckbox.checked = loadOptOut();
  inMemoryHistory = loadHistory();
});
