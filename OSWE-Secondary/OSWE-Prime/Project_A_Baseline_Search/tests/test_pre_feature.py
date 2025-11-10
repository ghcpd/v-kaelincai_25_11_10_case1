import os
import subprocess
import time
import json
import requests
from playwright.sync_api import sync_playwright

SERVER_PY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py'))
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_pre.txt'))
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data.json'))


def start_server():
    proc = subprocess.Popen(['python', SERVER_PY])
    time.sleep(1)
    return proc


def stop_server(proc):
    proc.terminate()
    proc.wait()


def load_tests():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def get_logs():
    if not os.path.exists(LOG_FILE):
        return ''
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def test_baseline_behaviors(tmp_path):
    proc = start_server()
    results = []
    try:
        tests = load_tests()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto('http://127.0.0.1:5001')

            # Focus + type should NOT show dropdown
            tc0 = tests[0]
            page.click('#searchInput')
            page.keyboard.type('pizza')
            # baseline has no dropdown element
            has_dropdown = page.query_selector('#historyDropdown') is not None
            results.append({'id': tc0['id'], 'expected': False, 'actual': has_dropdown})

            # Press enter triggers search
            tc1 = tests[1]
            page.fill('#searchInput', '')
            page.type('#searchInput', 'sushi')
            page.keyboard.press('Enter')
            time.sleep(0.3)
            logs = get_logs()
            # assert that the last search logged contains sushi
            results.append({'id': tc1['id'], 'expected': 'sushi', 'actual': 'sushi' in logs})

            # Persistence absence
            tc2 = tests[2]
            page.fill('#searchInput', '')
            page.type('#searchInput', 'burrito')
            page.keyboard.press('Enter')
            # reload
            page.reload()
            # Ensure there is no history key
            has_history_key = page.evaluate("() => window.localStorage.getItem('search_history') !== null")
            results.append({'id': tc2['id'], 'expected': False, 'actual': has_history_key})

            browser.close()

    finally:
        stop_server(proc)

    # Write results file
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results', 'results_pre.json'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # Additional metrics
    correctness_rate = sum(1 for r in results if r['expected'] == r['actual']) / len(results)
    metrics = {'correctness_rate': correctness_rate}
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results', 'metrics_pre.json')), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    assert all(r['expected'] == r['actual'] or (isinstance(r['expected'], bool) and r['expected'] == r['actual']) for r in results)
