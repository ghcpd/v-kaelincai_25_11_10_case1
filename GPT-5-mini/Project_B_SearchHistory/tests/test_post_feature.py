import json
import os
import time
import subprocess
import pytest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='session')
def server_proc():
    env = os.environ.copy()
    env['PORT'] = '8002'
    proc = subprocess.Popen(['python', str(ROOT / 'server' / 'server.py')], env=env)
    time.sleep(0.5)
    yield proc
    proc.terminate(); proc.wait()

def load_cases():
    return json.loads((ROOT / 'data' / 'test_data.json').read_text())

def run_case(browser, case):
    page = browser.new_page()
    page.goto('http://127.0.0.1:8002/')
    # set initial storage
    storage = case['initial_state'].get('storage')
    if storage is not None:
        page.evaluate('localStorage.setItem("search_history_v1", JSON.stringify(%s))' % json.dumps(storage))
        page.reload()
    lat_start = time.time()
    for act in case['actions']:
        a = act['action']
        if a == 'type':
            page.fill('#search', act['value'])
            time.sleep(0.05)
        elif a == 'key':
            page.keyboard.press(act['value'])
            time.sleep(0.05)
        elif a == 'focus':
            page.focus('#search'); time.sleep(0.05)
        elif a == 'reload':
            page.reload(); time.sleep(0.05)
    latency = (time.time() - lat_start)
    # collect outputs
    dropdown_visible = page.eval_on_selector('#history', 'el => getComputedStyle(el).display !== "none"')
    items = page.eval_on_selector_all('.history-item', 'els => els.map(e => e.textContent)')
    last_search = page.evaluate('window.__LAST_SEARCH')
    storage_after = page.evaluate('localStorage.getItem("search_history_v1")')
    try:
        storage_after = json.loads(storage_after) if storage_after else []
    except:
        storage_after = storage_after
    page.close()
    return {
        'id': case['id'], 'dropdown': bool(dropdown_visible), 'items': items, 'last_search': last_search, 'storage_after': storage_after, 'latency': latency
    }

def test_post_feature(server_proc):
    cases = load_cases()
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for c in cases:
            r = run_case(browser, c)
            # simple assertions based on expected
            exp = c['expected']
            if 'dropdown' in exp:
                assert r['dropdown'] == exp['dropdown']
            if 'items' in exp:
                assert r['items'][:len(exp['items'])] == exp['items']
            if 'last_search' in exp:
                assert r['last_search'] and r['last_search'].get('query') == exp['last_search']['query']
            results.append(r)
        browser.close()
    (ROOT / 'results').mkdir(exist_ok=True)
    (ROOT / 'results' / 'results_post.json').write_text(json.dumps(results, indent=2))
