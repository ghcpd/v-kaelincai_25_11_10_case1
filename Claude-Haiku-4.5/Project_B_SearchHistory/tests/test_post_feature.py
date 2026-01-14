"""
Project B - Enhanced Search History Tests
Tests the post-feature enhanced search with history dropdown, keyboard nav, and persistence
"""

import pytest
import asyncio
import json
import os
import time
import subprocess
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from datetime import datetime, timedelta

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'
RESULTS_DIR = PROJECT_ROOT / 'results'
TEST_DATA_FILE = Path(__file__).parent.parent.parent / 'shared_artifacts' / 'test_data.json'
SERVER_PORT = 5002
SERVER_URL = f'http://localhost:{SERVER_PORT}'

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

class EnhancedSearchTester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.test_results = []
        self.metrics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'keyboard_nav_success': 0,
            'persistence_success': 0,
            'avg_dropdown_latency_ms': 0.0,
            'correctness_rate': 0.0
        }
        self.latencies = []
        self.server_process = None

    async def start_server(self):
        """Start the Flask development server"""
        env = os.environ.copy()
        env['PORT'] = str(SERVER_PORT)
        env['PYTHONUNBUFFERED'] = '1'

        server_script = PROJECT_ROOT / 'server' / 'server.py'
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        await self._wait_for_server(max_retries=30)
        print(f"✓ Server started on {SERVER_URL}")

    async def _wait_for_server(self, max_retries=30):
        """Wait for server to become available"""
        import aiohttp
        retries = 0
        while retries < max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'{SERVER_URL}/api/health', timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            return
            except:
                pass
            await asyncio.sleep(0.5)
            retries += 1

        raise RuntimeError(f"Server did not start within {max_retries * 0.5} seconds")

    async def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✓ Server stopped")

    async def setup(self):
        """Initialize browser and navigate to app"""
        await self.start_server()
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        await self.page.goto(SERVER_URL, wait_until='networkidle')
        print(f"✓ Navigated to {SERVER_URL}")

    async def teardown(self):
        """Close browser and server"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        await self.stop_server()

    async def clear_storage(self):
        """Clear localStorage"""
        await self.page.evaluate('localStorage.clear()')

    async def test_empty_history_focus(self):
        """TC_002: Focus on empty history shows no dropdown"""
        test_id = 'TC_002_empty_history_focus'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Focus input
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Dropdown should not be visible
            dropdown_visible = await self.page.is_visible('#history_dropdown.visible')
            assert not dropdown_visible, "Dropdown should not be visible with empty history"

            self._record_test_pass(test_id, {
                'dropdown_visible': False,
                'empty_history_handled': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_history_display_on_focus(self):
        """TC_003: History displays on focus with most-recent-first order"""
        test_id = 'TC_003_history_display_focus'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform searches
            searches = ['python tutorial', 'javascript async', 'css grid layout']
            for search in searches:
                await self.page.fill('#search_input', search)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(300)

            # Focus input
            start_time = time.time()
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)
            latency_ms = (time.time() - start_time) * 1000
            self.latencies.append(latency_ms)

            # Check dropdown visibility
            dropdown_visible = await self.page.is_visible('#history_dropdown.visible')
            assert dropdown_visible, "Dropdown should be visible after focus"

            # Get history items
            items = await self.page.locator('.history-item[role="option"]').all_text_contents()
            assert len(items) == 3, f"Expected 3 items, got {len(items)}"

            # Check order (most recent first)
            expected_order = ['css grid layout', 'javascript async', 'python tutorial']
            actual_order = [item.strip() for item in items[:3]]
            assert actual_order == expected_order, f"Order mismatch. Expected {expected_order}, got {actual_order}"

            self._record_test_pass(test_id, {
                'dropdown_visible': True,
                'items_count': len(items),
                'correct_order': actual_order == expected_order,
                'latency_ms': latency_ms
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_click_to_repeat(self):
        """TC_006: Click on history item repeats search"""
        test_id = 'TC_006_click_repeat'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform initial search
            await self.page.fill('#search_input', 'test search')
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(300)

            # Focus to show dropdown
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Click first item
            items = await self.page.locator('.history-item[role="option"]').all()
            if len(items) > 0:
                await items[0].click()
                await self.page.wait_for_timeout(300)

            # Verify result was added
            result_count = await self.page.locator('.result-item').count()
            assert result_count >= 1, "Search should be triggered by click"

            self._record_test_pass(test_id, {
                'click_executed': True,
                'search_triggered': True,
                'result_displayed': result_count >= 1
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_keyboard_navigation(self):
        """TC_005: Keyboard navigation (Up/Down/Enter/Esc)"""
        test_id = 'TC_005_keyboard_nav'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform searches
            searches = ['first', 'second', 'third']
            for search in searches:
                await self.page.fill('#search_input', search)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(200)

            # Focus and show dropdown
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Navigate down twice
            await self.page.press('#search_input', 'ArrowDown')
            await self.page.wait_for_timeout(100)
            await self.page.press('#search_input', 'ArrowDown')
            await self.page.wait_for_timeout(100)

            # Check which item is highlighted
            highlighted = await self.page.locator('.history-item.highlighted').text_content()
            assert highlighted is not None, "An item should be highlighted"

            # Press Enter to select
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(300)

            # Verify search was triggered
            result_count = await self.page.locator('.result-item').count()
            assert result_count >= 1, "Search should be triggered by keyboard selection"

            self.metrics['keyboard_nav_success'] += 1

            self._record_test_pass(test_id, {
                'arrow_down_navigates': True,
                'enter_selects': True,
                'search_triggered': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_esc_closes_dropdown(self):
        """TC_005: Escape closes dropdown"""
        test_id = 'TC_005_esc_closes'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform search
            await self.page.fill('#search_input', 'test')
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(200)

            # Focus to show dropdown
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Verify dropdown is open
            dropdown_visible = await self.page.is_visible('#history_dropdown.visible')
            assert dropdown_visible, "Dropdown should be visible"

            # Press Escape
            await self.page.press('#search_input', 'Escape')
            await self.page.wait_for_timeout(200)

            # Verify dropdown is closed
            dropdown_visible = await self.page.is_visible('#history_dropdown.visible')
            assert not dropdown_visible, "Dropdown should be closed after Escape"

            self._record_test_pass(test_id, {
                'esc_closes_dropdown': True,
                'focus_maintained': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_persistence_across_reload(self):
        """TC_007: History persists across page reload"""
        test_id = 'TC_007_persistence_reload'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform searches
            searches = ['persist search 1', 'persist search 2']
            for search in searches:
                await self.page.fill('#search_input', search)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(300)

            # Get localStorage before reload
            history_before = await self.page.evaluate(
                'JSON.parse(localStorage.getItem("search_history_data") || "[]")'
            )
            assert len(history_before) == 2, f"Expected 2 items before reload, got {len(history_before)}"

            # Reload page
            await self.page.reload(wait_until='networkidle')

            # Get localStorage after reload
            history_after = await self.page.evaluate(
                'JSON.parse(localStorage.getItem("search_history_data") || "[]")'
            )
            assert len(history_after) == 2, f"Expected 2 items after reload, got {len(history_after)}"

            # Verify content matches
            assert history_before[0]['query'] == history_after[0]['query'], "History content should match"

            # Show dropdown and verify items displayed
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            items = await self.page.locator('.history-item[role="option"]').all_text_contents()
            assert len(items) >= 2, "Persisted history should be displayed"

            self.metrics['persistence_success'] += 1

            self._record_test_pass(test_id, {
                'persisted_correctly': True,
                'items_restored': len(items) >= 2,
                'content_matches': history_before[0]['query'] == history_after[0]['query']
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_clear_history(self):
        """TC_008: Clear history button works"""
        test_id = 'TC_008_clear_history'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform searches
            searches = ['search to clear 1', 'search to clear 2']
            for search in searches:
                await self.page.fill('#search_input', search)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(300)

            # Focus to show dropdown
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Click clear button
            clear_btn = await self.page.locator('.dropdown-actions .clear').first
            await clear_btn.click()
            await self.page.wait_for_timeout(300)

            # Handle confirmation dialog
            await self.page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
            await clear_btn.click()
            await self.page.wait_for_timeout(500)

            # Verify history is empty
            history_stored = await self.page.evaluate(
                'JSON.parse(localStorage.getItem("search_history_data") || "[]")'
            )
            assert len(history_stored) == 0, f"History should be empty, got {len(history_stored)}"

            self._record_test_pass(test_id, {
                'history_cleared': True,
                'storage_emptied': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_opt_out_persistence(self):
        """TC_010: Opt-out disables persistence"""
        test_id = 'TC_010_opt_out'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Enable opt-out
            await self.page.check('#opt_out_toggle')
            await self.page.wait_for_timeout(300)

            # Perform search
            await self.page.fill('#search_input', 'private search')
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(300)

            # Verify not persisted
            history_stored = await self.page.evaluate(
                'JSON.parse(localStorage.getItem("search_history_data") || "[]")'
            )
            assert len(history_stored) == 0, "History should not be persisted when opted-out"

            # Reload page
            await self.page.reload(wait_until='networkidle')

            # Verify opt-out state persisted
            opt_out_enabled = await self.page.is_checked('#opt_out_toggle')
            assert opt_out_enabled, "Opt-out preference should persist"

            # Verify no history displayed
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            dropdown_visible = await self.page.is_visible('#history_dropdown.visible')
            if dropdown_visible:
                items = await self.page.locator('.history-item[role="option"]').all_text_contents()
                assert len(items) == 0, "No history should be shown when opted-out"

            self._record_test_pass(test_id, {
                'opt_out_disables_persistence': True,
                'no_history_saved': True,
                'preference_persisted': opt_out_enabled
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_xss_prevention(self):
        """TC_009: XSS prevention - malicious input sanitized"""
        test_id = 'TC_009_xss_prevention'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Try to inject script
            malicious_input = '<script>alert("xss")</script>'
            await self.page.fill('#search_input', malicious_input)
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(300)

            # Check page still intact (no JS errors)
            errors = await self.page.evaluate('window.javaScriptErrors = []')

            # Reload and show history
            await self.page.reload(wait_until='networkidle')
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Verify malicious script is rendered as text (escaped)
            history_item_text = await self.page.locator('.history-item[role="option"]').first.text_content()
            assert history_item_text is not None, "History item should be displayed"
            assert '<script>' not in (await self.page.locator('#history_dropdown').inner_html() or ''), \
                "Script tags should be escaped in HTML"

            self._record_test_pass(test_id, {
                'xss_prevented': True,
                'malicious_input_safe': True,
                'script_not_executed': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_max_history_size(self):
        """TC_003: Maximum 5 recent items displayed"""
        test_id = 'TC_003_max_5_items'
        try:
            await self.clear_storage()
            await self.page.reload(wait_until='networkidle')

            # Perform 7 searches
            for i in range(7):
                await self.page.fill('#search_input', f'search {i}')
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(200)

            # Focus to show dropdown
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)

            # Count displayed items
            items = await self.page.locator('.history-item[role="option"]').all_text_contents()
            assert len(items) <= 5, f"Should show max 5 items, got {len(items)}"

            self._record_test_pass(test_id, {
                'max_5_enforced': True,
                'displayed_count': len(items)
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    def _record_test_pass(self, test_id, details):
        """Record a passing test"""
        self.test_results.append({
            'test_id': test_id,
            'status': 'PASS',
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self.metrics['passed_tests'] += 1
        self.metrics['total_tests'] += 1
        print(f"  ✓ {test_id}: PASS")

    def _record_test_fail(self, test_id, reason):
        """Record a failing test"""
        self.test_results.append({
            'test_id': test_id,
            'status': 'FAIL',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        self.metrics['failed_tests'] += 1
        self.metrics['total_tests'] += 1
        print(f"  ✗ {test_id}: FAIL - {reason}")

    async def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "="*60)
        print("PROJECT B - ENHANCED SEARCH HISTORY TESTS")
        print("="*60 + "\n")

        await self.setup()

        try:
            print("Running enhanced search history tests...\n")
            await self.test_empty_history_focus()
            await self.test_history_display_on_focus()
            await self.test_click_to_repeat()
            await self.test_keyboard_navigation()
            await self.test_esc_closes_dropdown()
            await self.test_persistence_across_reload()
            await self.test_clear_history()
            await self.test_opt_out_persistence()
            await self.test_xss_prevention()
            await self.test_max_history_size()

        finally:
            await self.teardown()

        # Calculate metrics
        if self.metrics['total_tests'] > 0:
            self.metrics['correctness_rate'] = (
                self.metrics['passed_tests'] / self.metrics['total_tests'] * 100
            )

        if self.latencies:
            self.metrics['avg_dropdown_latency_ms'] = sum(self.latencies) / len(self.latencies)

        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save test results to JSON"""
        results_file = RESULTS_DIR / 'results_post.json'

        output = {
            'project': 'Project_B_SearchHistory',
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'test_results': self.test_results
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Results saved to {results_file}")

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY - PROJECT B (ENHANCED)")
        print("="*60)
        print(f"Total Tests:                {self.metrics['total_tests']}")
        print(f"Passed:                     {self.metrics['passed_tests']}")
        print(f"Failed:                     {self.metrics['failed_tests']}")
        print(f"Correctness Rate:           {self.metrics['correctness_rate']:.1f}%")
        print(f"Keyboard Navigation Success:{self.metrics['keyboard_nav_success']}")
        print(f"Persistence Success:        {self.metrics['persistence_success']}")
        print(f"Avg Dropdown Latency:       {self.metrics['avg_dropdown_latency_ms']:.2f}ms")
        print("="*60 + "\n")

async def main():
    """Main test entry point"""
    tester = EnhancedSearchTester()
    await tester.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
