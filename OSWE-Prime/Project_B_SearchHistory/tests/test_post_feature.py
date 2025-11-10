import os, time, json, subprocess
import pytest
from playwright.sync_api import sync_playwright

SERVER_PY = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
TRACE_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'trace_post.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_post.txt')

def start_server():
    proc = subprocess.Popen(['python', SERVER_PY], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except Exception:
        proc.kill()

@pytest.fixture(scope='module')
def server():
    proc = start_server()
    time.sleep(0.6)
    yield
    stop_server(proc)

def read_traces():
    if os.path.exists(TRACE_FILE):
        with open(TRACE_FILE, 'r') as f:
            return json.load(f)
    return []

def test_search_history_dropdown_and_selection(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        # make initial searches
        page.fill('#search-input', 'alpha')
        page.keyboard.press('Enter')
        page.fill('#search-input', 'beta')
        page.keyboard.press('Enter')
        page.fill('#search-input', 'gamma')
        page.keyboard.press('Enter')
        time.sleep(0.2)
        # focus to show dropdown
        page.focus('#search-input')
        t0 = time.time()
        page.wait_for_selector('#history-dropdown')
        t1 = time.time()
        latency = t1 - t0
        # read items
        items = page.query_selector_all('#history-dropdown .history-item')
        texts = [it.inner_text() for it in items]
        assert 'gamma' in texts and 'beta' in texts and 'alpha' in texts
        # click second item (beta)
        # find 'beta'
        for it in items:
            if it.inner_text() == 'beta':
                it.click()
                break
        time.sleep(0.2)
        traces = read_traces()
        assert any(t['query'] == 'beta' for t in traces)
        # record result
        res = { 'id': 'dropdown_click_select', 'pass': True, 'latency': latency }
        with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json'), 'w') as f:
            json.dump([res], f)
        browser.close()

def test_keyboard_navigation(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        # seed history using localStorage directly
        page.evaluate("() => { localStorage.setItem('search_history_v1', JSON.stringify(['a','b','c','d','e','f'])); }")
        page.reload()
        page.focus('#search-input')
        page.wait_for_selector('#history-dropdown')
        # press ArrowDown twice -> highlights 'b'
        page.keyboard.press('ArrowDown')
        page.keyboard.press('ArrowDown')
        # Wait a bit and press Enter
        page.keyboard.press('Enter')
        time.sleep(0.2)
        traces = read_traces()
        # last search should be 'b'
        assert traces[-1]['query'] == 'b'
        res = { 'id': 'keyboard_navigation', 'pass': True }
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append(res)
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()

def test_persistence_and_opt_out(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        page.fill('#search-input', 'session-only')
        page.keyboard.press('Enter')
        time.sleep(0.2)
        # toggle persist to false
        page.click('#persist-toggle')
        page.reload()
        page.focus('#search-input')
        # dropdown should not show items because persistence is off
        # check localstorage
        persisted = page.evaluate("() => !!localStorage.getItem('search_history_v1')")
        assert persisted == False
        res = { 'id': 'persistence_opt_out', 'pass': True }
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append(res)
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()

def test_shared_cases(server):
    # Load canonical shared test vectors and run through them
    shared_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_test_data.json'))
    cases = json.load(open(shared_file))
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for c in cases:
            page.goto('http://localhost:8002/')
            # set initial state
            if c.get('initial_state', {}).get('history'):
                arr = c['initial_state']['history']
                page.evaluate("(a) => localStorage.setItem('search_history_v1', JSON.stringify(a))", arr)
            # perform actions
            ok = True
            for act in c['actions']:
                a = act['action']
                if a == 'type':
                    page.fill('#search-input', act['value'])
                elif a == 'enter':
                    page.keyboard.press('Enter')
                elif a == 'focus':
                    page.focus('#search-input')
                elif a == 'reload':
                    page.reload()
                elif a == 'toggle_persistence':
                    # set toggle to specified value (simulate click if needed to trigger event)
                    v = act['value']
                    cur = page.evaluate("() => document.getElementById('persist-toggle').checked")
                    if bool(cur) != bool(v):
                        page.click('#persist-toggle')
                elif a == 'key':
                    page.keyboard.press(act['value'])
                time.sleep(0.1)
            # evaluate expectations
            exp = c.get('expected', {})
            # check dropdown presence on focus
            page.focus('#search-input')
            t0 = time.time()
            try:
                page.wait_for_selector('#history-dropdown', timeout=1000)
                t1 = time.time()
                latency = t1 - t0
            except Exception:
                latency = None
            some_dropdown = page.query_selector('#history-dropdown')
            dropdown_visible = (some_dropdown and some_dropdown.evaluate('el => el.style.display !== "none"'))
            if exp.get('dropdown_present') != bool(dropdown_visible):
                ok = False
            # check item lists match expected where specified
            exp_items = exp.get('items')
            if exp_items and dropdown_visible:
                items_el = page.query_selector_all('#history-dropdown .history-item')
                texts = [it.inner_text() for it in items_el]
                # compare prefix since lengths may be > max
                if texts[:len(exp_items)] != exp_items:
                    ok = False
            rec = { 'id': c['id'], 'pass': ok }
            if latency is not None: rec['latency'] = latency
            results.append(rec)
        # write to results
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.extend(results)
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()

def test_clear_history(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        page.fill('#search-input', 'to-clear')
        page.keyboard.press('Enter')
        time.sleep(0.2)
        page.click('#clear-history')
        # check storage is empty
        v = page.evaluate("() => localStorage.getItem('search_history_v1')")
        assert v is None or v == '[]'
        # check dropdown hidden
        page.focus('#search-input')
        time.sleep(0.1)
        dd = page.query_selector('#history-dropdown')
        if dd:
            assert dd.evaluate('el => el.style.display') == 'none'
        # write result
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append({ 'id': 'clear_history', 'pass': True })
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()

def test_accessibility_roles(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        page.focus('#search-input')
        page.wait_for_selector('#history-dropdown')
        role = page.get_attribute('#history-dropdown', 'role')
        assert role == 'listbox'
        # check items have role option when present
        items = page.query_selector_all('#history-dropdown .history-item')
        for it in items:
            assert it.get_attribute('role') == 'option'
        browser.close()

def test_large_history_performance(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/')
        # Perform many searches quickly
        for i in range(20):
            page.fill('#search-input', f'item-{i}')
            page.keyboard.press('Enter')
        time.sleep(0.5)
        page.focus('#search-input')
        t0 = time.time()
        page.wait_for_selector('#history-dropdown')
        t1 = time.time()
        latency = t1 - t0
        # verify only last 5 items shown
        items = page.query_selector_all('#history-dropdown .history-item')
        texts = [it.inner_text() for it in items]
        assert texts[:5] == [f'item-{i}' for i in range(19, 14, -1)]
        # metrics write
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_post.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append({ 'id': 'large_history_perf', 'pass': True, 'latency': latency })
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()
