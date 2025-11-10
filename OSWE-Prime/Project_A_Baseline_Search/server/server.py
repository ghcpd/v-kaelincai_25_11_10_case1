from flask import Flask, send_from_directory, request, jsonify
import os, json, time

app = Flask(__name__, static_folder='../src', static_url_path='')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_pre.txt')
TRACE_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'trace_pre.json')

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(app.static_folder, path)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    entry = { 'query': data.get('query'), 'time': time.time() }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    # append to trace file
    traces = []
    if os.path.exists(TRACE_FILE):
        try:
            with open(TRACE_FILE, 'r') as tf:
                traces = json.load(tf)
        except Exception:
            traces = []
    traces.append(entry)
    with open(TRACE_FILE, 'w') as tf:
        json.dump(traces, tf)
    return jsonify(entry)

if __name__ == '__main__':
    app.run(port=8001)
