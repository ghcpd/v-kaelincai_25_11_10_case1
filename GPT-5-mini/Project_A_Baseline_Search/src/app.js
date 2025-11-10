(() => {
  const input = document.getElementById('search');
  const results = document.getElementById('results');

  function sendSearch(query) {
    // emulate sending a search request by dispatching a custom event and logging
    const payload = { query, timestamp: Date.now() };
    window.__LAST_SEARCH = payload;
    console.log('search-request', JSON.stringify(payload));
    results.textContent = 'Search sent: ' + query;
  }

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendSearch(input.value);
    }
  });
})();
