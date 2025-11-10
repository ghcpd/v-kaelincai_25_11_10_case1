import os, time, json, subprocess, signal
import pytest
from playwright.sync_api import sync_playwright
import requests
import threading
import http.client
from flask import Flask

SERVER_PY = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_pre.txt')
TRACE_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'trace_pre.json')

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

def load_test_data():
    shared = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_test_data.json'))
    with open(shared, 'r') as f:
        return json.load(f)

TEST_CASES = load_test_data()

def test_baseline_no_dropdown_and_enter_triggers_search(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8001/')
        # Focus input: should not show dropdown
        page.focus('#search-input')
        # Verify no dropdown present (baseline)
        assert page.query_selector('#history-dropdown') is None
        # Type and enter
        page.fill('#search-input', 'hello world')
        page.keyboard.press('Enter')
        # Wait for server to record
        time.sleep(0.2)
        traces = read_traces()
        assert any(t['query']=='hello world' for t in traces)
        res = { 'id': 'baseline_enter_search', 'pass': True }
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_pre.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append(res)
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()

def test_typing_does_not_trigger_search(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8001/')
        page.fill('#search-input', 'typing-only')
        time.sleep(0.2)
        traces = read_traces()
        # typing alone should not add search
        assert not any(t['query']=='typing-only' for t in traces)
        res = { 'id': 'baseline_no_dropdown_typing', 'pass': True }
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_pre.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.append(res)
        with open(rfile, 'w') as f: json.dump(prev, f)
    browser.close()

def test_shared_cases_baseline(server):
    shared_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_test_data.json'))
    cases = json.load(open(shared_file))
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for c in cases:
            page.goto('http://localhost:8001/')
            # apply initial state by clearing localStorage (baseline has no history UI)
            if c.get('initial_state', {}).get('history'):
                arr = c['initial_state']['history']
                page.evaluate("(a) => { localStorage.setItem('search_history_v1', JSON.stringify(a)); }", arr)
            # perform actions
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
                elif a == 'key':
                    page.keyboard.press(act['value'])
                time.sleep(0.1)
            # baseline should never show dropdown
            has_dropdown = page.query_selector('#history-dropdown') is not None
            ok = not has_dropdown
            results.append({ 'id': c['id'], 'pass': ok })
        rfile = os.path.join(os.path.dirname(__file__), '..', 'results', 'results_pre.json')
        prev = []
        if os.path.exists(rfile):
            with open(rfile, 'r') as f: prev = json.load(f)
        prev.extend(results)
        with open(rfile, 'w') as f: json.dump(prev, f)
        browser.close()
