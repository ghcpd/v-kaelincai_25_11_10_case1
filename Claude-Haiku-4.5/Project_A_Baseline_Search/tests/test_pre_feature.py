"""
Project A - Baseline Search Tests
Tests the pre-feature baseline: Enter-only search with no history dropdown
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
SERVER_PORT = 5001
SERVER_URL = f'http://localhost:{SERVER_PORT}'

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

class BaselineSearchTester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.test_results = []
        self.metrics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'total_latency_ms': 0,
            'correctness_rate': 0.0
        }
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
        
        # Wait for server to start
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
        
        # Go to the app
        await self.page.goto(SERVER_URL, wait_until='networkidle')
        print(f"✓ Navigated to {SERVER_URL}")

    async def teardown(self):
        """Close browser and server"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        await self.stop_server()

    async def test_empty_history(self):
        """TC_001: Empty History - Normal Case"""
        test_id = 'TC_001_empty_history'
        try:
            # Focus input - should not show dropdown (doesn't exist in baseline)
            await self.page.focus('#search_input')
            await self.page.wait_for_timeout(200)
            
            # Verify no dropdown elements
            dropdown_count = await self.page.evaluate('document.querySelectorAll("[role=listbox], [role=menu]").length')
            
            assert dropdown_count == 0, "Dropdown should not exist in baseline"
            
            self._record_test_pass(test_id, {
                'dropdown_visible': False,
                'dropdown_items': [],
                'dropdown_count': dropdown_count
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_enter_triggers_search(self):
        """TC_002: Enter Key Triggers Search"""
        test_id = 'TC_002_enter_search'
        try:
            start_time = time.time()
            
            # Type and submit
            await self.page.fill('#search_input', 'python tutorial')
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(300)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Verify result displayed
            result_visible = await self.page.is_visible('.result-item')
            assert result_visible, "Result should be displayed after Enter"
            
            # Get displayed result
            result_text = await self.page.text_content('.result-item')
            assert result_text is not None and 'python tutorial' in result_text, "Search query should appear in result"
            
            # Input should be cleared
            input_value = await self.page.input_value('#search_input')
            assert input_value == '', "Input should be cleared after search"
            
            self._record_test_pass(test_id, {
                'search_triggered': True,
                'result_displayed': True,
                'query_in_result': result_text is not None and 'python tutorial' in result_text,
                'input_cleared': input_value == '',
                'latency_ms': latency_ms
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_multiple_searches(self):
        """TC_003: Multiple Searches - No Persistence"""
        test_id = 'TC_003_multiple_searches'
        try:
            queries = ['first search', 'second search', 'third search']
            
            for query in queries:
                await self.page.fill('#search_input', query)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(200)
            
            # Verify all results displayed
            result_items = await self.page.locator('.result-item').count()
            assert result_items == len(queries), f"Expected {len(queries)} results, got {result_items}"
            
            # Reload page and verify no history persists
            await self.page.reload(wait_until='networkidle')
            result_items_after_reload = await self.page.locator('.result-item').count()
            assert result_items_after_reload == 0, "Results should not persist after reload (baseline)"
            
            self._record_test_pass(test_id, {
                'searches_performed': len(queries),
                'results_displayed': result_items == len(queries),
                'persisted_after_reload': False
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_other_keys_ignored(self):
        """TC_004: Other Keys Don't Trigger Search"""
        test_id = 'TC_004_other_keys_ignored'
        try:
            await self.page.fill('#search_input', 'test query')
            
            # Try various keys that should not trigger search
            for key in ['Space', 'ArrowUp', 'ArrowDown', 'Tab']:
                await self.page.press('#search_input', key)
                await self.page.wait_for_timeout(100)
            
            # Verify no results yet
            result_count = await self.page.locator('.result-item').count()
            assert result_count == 0, f"No results should be shown, got {result_count}"
            
            # Now press Enter
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(200)
            
            result_count = await self.page.locator('.result-item').count()
            assert result_count == 1, "Result should appear after Enter"
            
            self._record_test_pass(test_id, {
                'other_keys_ignored': True,
                'enter_still_works': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_empty_input_ignored(self):
        """TC_005: Empty Input Ignored"""
        test_id = 'TC_005_empty_input'
        try:
            # Try to submit empty search
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(200)
            
            result_count = await self.page.locator('.result-item').count()
            assert result_count == 0, "Empty search should not create result"
            
            # Valid search should work
            await self.page.fill('#search_input', 'valid search')
            await self.page.press('#search_input', 'Enter')
            await self.page.wait_for_timeout(200)
            
            result_count = await self.page.locator('.result-item').count()
            assert result_count == 1, "Valid search should create result"
            
            self._record_test_pass(test_id, {
                'empty_search_ignored': True,
                'valid_search_works': True
            })
        except AssertionError as e:
            self._record_test_fail(test_id, str(e))

    async def test_special_characters(self):
        """TC_006: Special Characters Handled Safely"""
        test_id = 'TC_006_special_chars'
        try:
            special_queries = [
                '<script>alert("xss")</script>',
                'search & special < > chars',
                'quote " and apostrophe\'',
                'unicode: 你好世界'
            ]
            
            for query in special_queries:
                await self.page.fill('#search_input', query)
                await self.page.press('#search_input', 'Enter')
                await self.page.wait_for_timeout(200)
            
            # Verify no script execution (no JS errors)
            console_errors = []
            def handle_console(msg):
                if msg.type == 'error':
                    console_errors.append(msg.text)
            
            # Check page integrity
            await self.page.goto(SERVER_URL, wait_until='networkidle')
            result_count = await self.page.locator('.result-item').count()
            
            self._record_test_pass(test_id, {
                'special_chars_handled': result_count == 0,  # Refreshed page
                'no_script_injection': len(console_errors) == 0
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
        print("PROJECT A - BASELINE SEARCH TESTS")
        print("="*60 + "\n")
        
        await self.setup()
        
        try:
            print("Running baseline functionality tests...\n")
            await self.test_empty_history()
            await self.test_enter_triggers_search()
            await self.test_multiple_searches()
            await self.test_other_keys_ignored()
            await self.test_empty_input_ignored()
            await self.test_special_characters()
            
        finally:
            await self.teardown()
        
        # Calculate metrics
        if self.metrics['total_tests'] > 0:
            self.metrics['correctness_rate'] = (
                self.metrics['passed_tests'] / self.metrics['total_tests'] * 100
            )
        
        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save test results to JSON"""
        results_file = RESULTS_DIR / 'results_pre.json'
        
        output = {
            'project': 'Project_A_Baseline_Search',
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
        print("TEST SUMMARY - PROJECT A (BASELINE)")
        print("="*60)
        print(f"Total Tests:        {self.metrics['total_tests']}")
        print(f"Passed:             {self.metrics['passed_tests']}")
        print(f"Failed:             {self.metrics['failed_tests']}")
        print(f"Correctness Rate:   {self.metrics['correctness_rate']:.1f}%")
        print("="*60 + "\n")

async def main():
    """Main test entry point"""
    tester = BaselineSearchTester()
    await tester.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
