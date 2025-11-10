/**
 * Project B - Search History Dropdown with Persistence and Privacy Controls
 * Features:
 * - Show 5 most recent searches on focus/typing
 * - Keyboard navigation (Up/Down/Enter/Esc)
 * - Click to repeat search
 * - Persist history to localStorage
 * - Privacy: opt-out toggle, clear history button
 * - XSS protection and sanitization
 */

class SearchHistoryManager {
    constructor() {
        this.searchInput = document.getElementById('search_input');
        this.historyDropdown = document.getElementById('history_dropdown');
        this.resultsContainer = document.getElementById('results');
        this.optOutToggle = document.getElementById('opt_out_toggle');
        this.successMessage = document.getElementById('success_message');

        this.history = [];
        this.highlightedIndex = -1;
        this.isDropdownOpen = false;
        this.maxHistorySize = 50;
        this.maxRecentShown = 5;
        
        // Storage configuration
        this.storageKey = 'search_history_data';
        this.optOutKey = 'search_history_opt_out';

        this.init();
    }

    init() {
        this.loadHistoryFromStorage();
        this.loadOptOutState();
        this.setupEventListeners();
        this.logEvent('Application initialized');
    }

    setupEventListeners() {
        // Input focus shows dropdown
        this.searchInput.addEventListener('focus', () => {
            this.showDropdown();
        });

        // Input typing updates dropdown
        this.searchInput.addEventListener('input', () => {
            if (this.searchInput.value.trim()) {
                this.showDropdown();
            }
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (!this.isDropdownOpen && e.key !== 'Enter') {
                return;
            }

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.highlightNext();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.highlightPrevious();
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (this.isDropdownOpen && this.highlightedIndex >= 0) {
                        this.selectHighlighted();
                    } else if (this.searchInput.value.trim()) {
                        this.performSearch();
                    }
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.closeDropdown();
                    this.searchInput.focus();
                    break;
            }
        });

        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) {
                this.closeDropdown();
            }
        });

        // Opt-out toggle
        this.optOutToggle.addEventListener('change', () => {
            this.saveOptOutState();
            this.logEvent(`History persistence toggled: ${!this.optOutToggle.checked}`);
        });
    }

    showDropdown() {
        if (!this.history.length) {
            this.isDropdownOpen = false;
            this.historyDropdown.classList.remove('visible');
            return;
        }

        this.renderDropdown();
        this.isDropdownOpen = true;
        this.historyDropdown.classList.add('visible');
        this.searchInput.setAttribute('aria-expanded', 'true');
    }

    closeDropdown() {
        this.isDropdownOpen = false;
        this.highlightedIndex = -1;
        this.historyDropdown.classList.remove('visible');
        this.searchInput.setAttribute('aria-expanded', 'false');
    }

    renderDropdown() {
        this.historyDropdown.innerHTML = '';

        const recentItems = this.getRecentHistory();

        if (recentItems.length === 0) {
            this.historyDropdown.innerHTML = '<li class="history-empty">No search history</li>';
            return;
        }

        // Render history items
        recentItems.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'history-item';
            li.setAttribute('role', 'option');
            li.setAttribute('data-index', index);
            li.textContent = this.truncate(item.query, 80);
            
            li.addEventListener('click', () => {
                this.highlightedIndex = index;
                this.selectHighlighted();
            });

            li.addEventListener('mouseenter', () => {
                this.clearHighlight();
                li.classList.add('highlighted');
                this.highlightedIndex = index;
            });

            this.historyDropdown.appendChild(li);
        });

        // Add action buttons
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'dropdown-actions';

        const clearBtn = document.createElement('button');
        clearBtn.className = 'clear';
        clearBtn.textContent = '🗑 Clear History';
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearHistory();
        });
        actionsDiv.appendChild(clearBtn);

        this.historyDropdown.appendChild(actionsDiv);
    }

    getRecentHistory() {
        return this.history.slice(-this.maxRecentShown).reverse();
    }

    highlightNext() {
        const maxIndex = this.getRecentHistory().length - 1;
        if (this.highlightedIndex < maxIndex) {
            this.clearHighlight();
            this.highlightedIndex++;
            this.updateHighlightUI();
        }
    }

    highlightPrevious() {
        if (this.highlightedIndex > 0) {
            this.clearHighlight();
            this.highlightedIndex--;
            this.updateHighlightUI();
        }
    }

    clearHighlight() {
        document.querySelectorAll('.history-item.highlighted').forEach(el => {
            el.classList.remove('highlighted');
        });
    }

    updateHighlightUI() {
        this.clearHighlight();
        const item = document.querySelector(`.history-item[data-index="${this.highlightedIndex}"]`);
        if (item) {
            item.classList.add('highlighted');
            item.scrollIntoView({ block: 'nearest' });
        }
    }

    selectHighlighted() {
        if (this.highlightedIndex >= 0 && this.highlightedIndex < this.getRecentHistory().length) {
            const recentItems = this.getRecentHistory();
            const selected = recentItems[this.highlightedIndex];
            this.searchInput.value = selected.query;
            this.performSearch(selected.query);
            this.closeDropdown();
        }
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
            method: 'SEARCH'
        };

        // Add to history if persistence enabled
        if (!this.optOutToggle.checked) {
            this.addToHistory(query);
        }

        this.displayResult(searchPayload);
        this.closeDropdown();
        this.logEvent(`Search executed: ${query}`);

        // Clear input for next search
        this.searchInput.value = '';
        this.searchInput.focus();
    }

    addToHistory(query) {
        // Remove if duplicate (will re-add at end)
        this.history = this.history.filter(h => h.query !== query);

        // Add new entry
        this.history.push({
            query: query,
            timestamp: new Date().toISOString()
        });

        // Trim if exceeds max size
        if (this.history.length > this.maxHistorySize) {
            this.history = this.history.slice(-this.maxHistorySize);
        }

        this.saveHistoryToStorage();
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

        if (this.resultsContainer.children.length > 0 &&
            this.resultsContainer.children[0].innerHTML.includes('No searches')) {
            this.resultsContainer.innerHTML = '';
        }

        this.resultsContainer.insertBefore(resultItem, this.resultsContainer.firstChild);
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all search history?')) {
            this.history = [];
            this.saveHistoryToStorage();
            this.closeDropdown();
            this.showSuccessMessage('History cleared');
            this.logEvent('Search history cleared by user');
        }
    }

    saveHistoryToStorage() {
        if (!this.optOutToggle.checked) {
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(this.history));
            } catch (e) {
                this.logEvent(`Storage error: ${e.message}`);
            }
        }
    }

    loadHistoryFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                this.history = JSON.parse(stored);
            }
        } catch (e) {
            this.logEvent(`Failed to load history: ${e.message}`);
            this.history = [];
        }
    }

    saveOptOutState() {
        try {
            localStorage.setItem(this.optOutKey, JSON.stringify(this.optOutToggle.checked));
            if (this.optOutToggle.checked) {
                // Clear history when opting out
                this.history = [];
                localStorage.removeItem(this.storageKey);
            }
        } catch (e) {
            this.logEvent(`Failed to save opt-out state: ${e.message}`);
        }
    }

    loadOptOutState() {
        try {
            const stored = localStorage.getItem(this.optOutKey);
            if (stored !== null) {
                this.optOutToggle.checked = JSON.parse(stored);
            }
        } catch (e) {
            this.logEvent(`Failed to load opt-out state: ${e.message}`);
        }
    }

    showSuccessMessage(msg) {
        this.successMessage.textContent = `✓ ${msg}`;
        this.successMessage.classList.add('show');
        setTimeout(() => {
            this.successMessage.classList.remove('show');
        }, 2000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncate(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '…' : text;
    }

    logEvent(message) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${message}`);
    }

    getHistory() {
        return this.history;
    }

    getPublicState() {
        return {
            history: this.history,
            isDropdownOpen: this.isDropdownOpen,
            optOutEnabled: this.optOutToggle.checked
        };
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SearchHistoryManager();
});
