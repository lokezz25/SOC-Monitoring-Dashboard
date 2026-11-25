"""Flask application entry point for SOC Monitoring Dashboard"""
import sys, os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Register blueprints (API routes)
from routes.alerts import alerts_bp
from routes.incidents import incidents_bp
from routes.agents import agents_bp
from routes.reports import reports_bp
from routes.simulation import simulation_bp
from routes.mitre import mitre_bp

app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(agents_bp, url_prefix='/api/agents')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(mitre_bp, url_prefix='/api/mitre')
# Register simulation routes
app.register_blueprint(simulation_bp, url_prefix='/api/simulation')

# Catch-all for unknown API routes to return 404 JSON instead of static 405
@app.route('/api/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def api_not_found(subpath):
    return jsonify({'error': f'API route /api/{subpath} not found'}), 404

# Serve frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Ensure database exists
    from database import init_db
    init_db()
    # Run the development server
    app.run(host='0.0.0.0', port=5001, debug=False)
