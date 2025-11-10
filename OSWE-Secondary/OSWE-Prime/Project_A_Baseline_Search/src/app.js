const input = document.getElementById('searchInput');
const results = document.getElementById('results');

function log(msg) { console.info('[APP]', msg); }

input.addEventListener('keydown', async (e) => {
  if (e.key === 'Enter') {
    const q = input.value.trim();
    if (!q) return;
    log('Search triggered: ' + q);
    const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    results.textContent = 'Search Results: ' + JSON.stringify(data);
  }
});