const input = document.getElementById('search-input');
const output = document.getElementById('output');

function performSearch(query) {
  // POST to server /search
  fetch('/search', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ query }) })
    .then(r => r.json())
    .then(data => {
      output.textContent = `Search performed: ${data.query}`;
    })
    .catch(err => {
      console.error('search error', err);
    });
}

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    performSearch(input.value);
  }
});
