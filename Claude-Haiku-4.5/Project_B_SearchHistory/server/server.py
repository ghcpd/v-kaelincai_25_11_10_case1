"""
Project B - Enhanced Search Server
Lightweight Flask server to serve the enhanced search application with history dropdown
"""

from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sys
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'src'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'src'),
    static_url_path='')

# Ensure logs directory exists
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Server request log
SERVER_LOG_FILE = os.path.join(logs_dir, 'server.log')

def log_request(message):
    """Log server events to file and console"""
    timestamp = datetime.now().isoformat()
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(SERVER_LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

@app.route('/')
def index():
    """Serve the enhanced search application"""
    log_request("GET / - Serving index.html")
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'src'),
        'index.html'
    )

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    log_request(f"GET /{filename} - Serving static file")
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'src'),
        filename
    )

@app.route('/api/health')
def health():
    """Health check endpoint"""
    log_request("GET /api/health - Health check")
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

@app.errorhandler(404)
def not_found(error):
    log_request(f"404 Not Found: {request.path}")
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def server_error(error):
    log_request(f"500 Server Error: {str(error)}")
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log_request(f"Starting Project B server on port {port}")
    app.run(host='127.0.0.1', port=port, debug=False)
