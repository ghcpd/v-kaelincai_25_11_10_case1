from flask import Flask, request, jsonify, send_from_directory
import logging
import os

app = Flask(__name__, static_folder='../src', static_url_path='/static')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'log_post.txt')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

@app.route('/')
def index():
    return send_from_directory('../src', 'index.html')

@app.route('/search')
def search():
    q = request.args.get('q')
    logging.info(f"Received search request: q={q}")
    return jsonify({'query': q, 'results': [f"{q} result 1"]})

if __name__ == '__main__':
    app.run(port=5002, debug=False)
