/**
 * Project A - Baseline Search Application
 * Simple search that triggers only on Enter key press
 * No history dropdown, no persistence
 */

class BaselineSearch {
    constructor() {
        this.searchInput = document.getElementById('search_input');
        this.resultsContainer = document.getElementById('results');
        this.searchHistory = [];
        
        this.setupEventListeners();
        this.logEvent('Application initialized');
    }

    setupEventListeners() {
        // Only trigger search on Enter key
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
    }

    performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.logEvent('Search attempted with empty query - rejected');
            return;
        }

        const searchPayload = {
            query: query,
            timestamp: new Date().toISOString(),
            method: 'ENTER_KEY'
        };

        this.searchHistory.push(searchPayload);
        this.displayResult(searchPayload);
        this.logEvent(`Search executed: ${query}`);
        
        // Clear input for next search
        this.searchInput.value = '';
        this.searchInput.focus();
    }

    displayResult(searchPayload) {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <div class="label">Search Result</div>
            <div class="value"><strong>Query:</strong> ${this.escapeHtml(searchPayload.query)}</div>
            <div class="value"><strong>Method:</strong> ${searchPayload.method}</div>
            <div class="timestamp">Timestamp: ${searchPayload.timestamp}</div>
        `;
        
        // Insert at top
        if (this.resultsContainer.children.length > 0 && 
            this.resultsContainer.children[0].innerHTML.includes('No searches')) {
            this.resultsContainer.innerHTML = '';
        }
        
        this.resultsContainer.insertBefore(resultItem, this.resultsContainer.firstChild);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    logEvent(message) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${message}`);
    }

    getSearchHistory() {
        return this.searchHistory;
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BaselineSearch();
});
