import os
import subprocess
import time
import json
import pathlib
from playwright.sync_api import sync_playwright

SERVER_PY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py'))
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_post.txt'))
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'test_data.json'))


def start_server():
    proc = subprocess.Popen(['python', SERVER_PY])
    time.sleep(1)
    return proc


def stop_server(proc):
    proc.terminate()
    proc.wait()


def load_tests():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def clear_logs():
    try:
        open(LOG_FILE, 'w').close()
    except Exception:
        pass


def get_logs():
    if not os.path.exists(LOG_FILE):
        return ''
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def set_local_storage(page, key, value):
    page.evaluate(f"() => localStorage.setItem('{key}', JSON.stringify({json.dumps(value)}))")


def run_case(page, case):
    metrics = {"id": case['id'], "pass": True, 'notes': [], 'latency': None}
    # apply initial state
    initial = case.get('initial_state', {})
    ls = initial.get('localStorage')
    if ls is not None:
        page.evaluate("(v) => localStorage.setItem('search_history', JSON.stringify(v))", ls)
    # open page
    page.goto('http://127.0.0.1:5002')

    # run actions
    for a in case.get('actions', []):
        if a['action'] == 'focus':
            start = time.monotonic()
            page.click('#searchInput')
            # wait for dropdown visible or a short timeout
            try:
                page.wait_for_selector('#historyDropdown:not([hidden])', timeout=1500)
                metrics['latency'] = time.monotonic() - start
            except Exception:
                # not visible
                metrics['latency'] = None
        elif a['action'] == 'type':
            page.fill('#searchInput', '')
            page.type('#searchInput', a['text'])
        elif a['action'] == 'enter':
            # wait for response
            with page.expect_response("**/search*") as resp:
                page.keyboard.press('Enter')
            res = resp.value
            metrics['last_search_payload'] = ''
            try:
                j = res.json()
                metrics['last_search_payload'] = j.get('query')
            except Exception:
                pass
            time.sleep(0.1)
        elif a['action'] == 'reload':
            page.reload()
        elif a['action'] == 'key':
            page.keyboard.press(a['key'])
        elif a['action'] == 'click_item':
            page.click(a['selector'])
        elif a['action'] == 'click':
            # generic click on a selector
            page.click(a['selector'])
    # verify expectations
    expected = case.get('expected', {})
    # dropdown appears
    if expected.get('dropdown'):
        visible = page.query_selector('#historyDropdown:not([hidden])') is not None
        if not visible:
            metrics['pass'] = False
            metrics['notes'].append('dropdown not visible')
    if 'items' in expected:
        items = page.query_selector_all('#historyDropdown .dropdown-item')
        texts = [i.text_content().strip() for i in items]
        # expected order exact
        if texts[:len(expected['items'])] != expected['items']:
            metrics['pass'] = False
            metrics['notes'].append({'expected': expected['items'], 'actual': texts})
    if 'items_contains' in expected:
        items = [i.text_content().strip() for i in page.query_selector_all('#historyDropdown .dropdown-item')]
        for s in expected['items_contains']:
            if not any(s in it for it in items):
                metrics['pass'] = False
                metrics['notes'].append(f'missing {s} in dropdown')
    if 'search_payload' in expected:
        # check last_search_payload
        if metrics.get('last_search_payload') != expected['search_payload']:
            metrics['pass'] = False
            metrics['notes'].append({'expected_search': expected['search_payload'], 'actual': metrics.get('last_search_payload')})
    if 'persistence' in expected:
        # check localStorage after reload
        page.reload()
        persisted = page.evaluate("() => JSON.parse(localStorage.getItem('search_history') || '[]')")
        metrics['persistence'] = len(persisted) > 0
        if not metrics['persistence']:
            metrics['pass'] = False
            metrics['notes'].append('persistence failed')
    if expected.get('aria_selected'):
        # check that some item has aria-selected true
        has = page.evaluate("() => !!document.querySelector('#historyDropdown .dropdown-item[aria-selected=\"true\"]')")
        if not has:
            metrics['pass'] = False
            metrics['notes'].append('aria-selected not set during keyboard nav')
    return metrics


def test_enhanced_behavior(tmp_path):
    proc = start_server()
    clear_logs()
    results = []
    try:
        tests = load_tests()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            for tc in tests:
                results.append(run_case(page, tc))
            browser.close()
    finally:
        stop_server(proc)

    out = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # compute metrics
    correctness_rate = sum(1 for r in results if r.get('pass')) / len(results)
    keyboard_success = sum(1 for r in results if r.get('id') == 'keyboard_navigation' and r.get('pass'))
    keyboard_total = sum(1 for r in results if r.get('id') == 'keyboard_navigation')
    keyboard_rate = keyboard_success / (keyboard_total or 1)
    persist_cases = [r for r in results if 'persistence' in r or r.get('id') in ('opt_out_disables_persistence','persistence_and_opt_out')]
    persist_success = sum(1 for r in persist_cases if r.get('persistence'))
    persist_rate = persist_success / (len(persist_cases) or 1)
    latencies = [r.get('latency') for r in results if r.get('latency')]
    avg_latency = sum(latencies) / len(latencies) if len(latencies) else None
    metrics = {
        'correctness_rate': correctness_rate,
        'keyboard_navigation_success': keyboard_rate,
        'persistence_success_rate': persist_rate,
        'avg_time_to_dropdown': avg_latency
    }
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results', 'metrics_post.json')), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    assert correctness_rate >= 0.6
