const input = document.getElementById('search-input');
const dropdown = document.getElementById('history-dropdown');
const output = document.getElementById('output');
const clearBtn = document.getElementById('clear-history');
const persistToggle = document.getElementById('persist-toggle');

const STORAGE_KEY = 'search_history_v1';
const MAX_ITEMS = 5;

function loadStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(x => typeof x === 'string');
  } catch (e) {
    return [];
  }
}

let history = loadStorage();
let sessionHistory = [];
let persist = persistToggle.checked;
let highlightedIndex = -1;

function saveStorage() {
  if (!persist) return;
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(history)); } catch(e) { console.warn('storage error', e); }
}

function addSearchToHistory(q) {
  if (typeof q !== 'string') return;
  q = q.trim();
  if (q === '') return;
  // dedupe existing
  history = history.filter(item => item !== q);
  history.unshift(q);
  // keep max
  if (history.length > MAX_ITEMS) history = history.slice(0, MAX_ITEMS);
  if (persist) saveStorage();
}

function showDropdown(filter='') {
  // source: storage + sessionHistory
  const combined = (history.concat(sessionHistory)).filter(x => typeof x === 'string');
  // dedupe keeping first occurrence
  const seen = new Set();
  const items = combined.filter(x => { if (seen.has(x)) return false; seen.add(x); return !filter || x.toLowerCase().includes(filter.toLowerCase()); }).slice(0, MAX_ITEMS);
  renderDropdown(items);
}

function renderDropdown(items) {
  dropdown.innerHTML = '';
  if (!items.length) {
    dropdown.style.display = 'none';
    dropdown.setAttribute('aria-hidden', 'true');
    return;
  }
  items.forEach((it, idx) => {
    const el = document.createElement('div');
    el.textContent = it;
    el.className = 'history-item';
    el.setAttribute('role', 'option');
    el.dataset.value = it;
    el.setAttribute('aria-selected', 'false');
    el.addEventListener('click', () => {
      performSearch(it);
    });
    dropdown.appendChild(el);
  });
  dropdown.style.display = 'block';
  dropdown.setAttribute('aria-hidden', 'false');
  highlightedIndex = -1;
}

function hideDropdown() {
  dropdown.style.display = 'none';
  dropdown.setAttribute('aria-hidden', 'true');
  highlightedIndex = -1;
}

function highlight(index) {
  const items = dropdown.querySelectorAll('.history-item');
  if (!items.length) return;
  if (index < 0) index = items.length - 1;
  if (index >= items.length) index = 0;
  items.forEach((it, idx) => it.setAttribute('aria-selected', idx === index ? 'true' : 'false'));
  highlightedIndex = index;
}

function selectedValue() {
  const selected = dropdown.querySelector('.history-item[aria-selected="true"]');
  return selected ? selected.dataset.value : null;
}

function performSearch(q) {
  if (!q) return;
  fetch('/search', { method: 'POST', headers: { 'Content-Type': 'application/json'}, body: JSON.stringify({ query: q }) })
    .then(r => r.json())
    .then(data => output.textContent = `Search: ${data.query}`)
    .catch(err => console.error(err));
  // add to history
  if (persist) addSearchToHistory(q); else sessionHistory.unshift(q);
  hideDropdown();
}

input.addEventListener('focus', () => { showDropdown(''); });
input.addEventListener('input', (e) => { showDropdown(e.target.value); });
input.addEventListener('keydown', (e) => {
  if (dropdown.style.display === 'none') return;
  if (e.key === 'ArrowDown') { e.preventDefault(); highlight((highlightedIndex || 0) + 1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); highlight((highlightedIndex || -1) - 1); }
  else if (e.key === 'Enter') { e.preventDefault(); const v = selectedValue(); if (v) performSearch(v); else performSearch(input.value); }
  else if (e.key === 'Escape') { e.preventDefault(); hideDropdown(); }
});

clearBtn.addEventListener('click', () => { history = []; sessionHistory = []; saveStorage(); hideDropdown(); });
persistToggle.addEventListener('change', () => { persist = persistToggle.checked; if (!persist) { // remove storage content
  try { localStorage.removeItem(STORAGE_KEY); } catch(e) {} } else saveStorage(); });

document.addEventListener('click', (e) => { if (!dropdown.contains(e.target) && e.target !== input) hideDropdown(); });

// expose for tests
window.__search_history = {
  _getHistory: () => history,
  _getSession: () => sessionHistory,
  _clear: () => { history = []; sessionHistory = []; saveStorage(); },
  _setPersist: (v) => { persistToggle.checked = !!v; persist = !!v; }
}
