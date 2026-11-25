from flask import Blueprint, request, jsonify, current_app
import sqlite3
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

def get_db():
    from database import get_connection
    return get_connection()

@alerts_bp.route('', methods=['GET'])
@alerts_bp.route('/', methods=['GET'])
def list_alerts():
    conn = get_db()
    cur = conn.cursor()
    # Filters
    severity = request.args.get('severity')
    status = request.args.get('status')
    category = request.args.get('category')
    query = 'SELECT * FROM alerts WHERE 1=1'
    params = []
    if severity:
        query += ' AND severity = ?'
        params.append(severity)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if category:
        query += ' AND category = ?'
        params.append(category)
    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@alerts_bp.route('/<alert_id>', methods=['GET'])
def get_alert(alert_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM alerts WHERE alert_id = ?', (alert_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Alert not found'}), 404

@alerts_bp.route('/<alert_id>/status', methods=['PUT'])
def update_alert_status(alert_id):
    data = request.json or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Missing status'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE alerts SET status = ? WHERE alert_id = ?', (new_status, alert_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Status updated'})

@alerts_bp.route('/statistics', methods=['GET'])
def alert_statistics():
    conn = get_db()
    cur = conn.cursor()
    # total alerts per severity
    cur.execute('SELECT severity, COUNT(*) as count FROM alerts GROUP BY severity')
    severity_counts = {row['severity']: row['count'] for row in cur.fetchall()}
    # total alerts per category
    cur.execute('SELECT category, COUNT(*) as count FROM alerts GROUP BY category')
    category_counts = {row['category']: row['count'] for row in cur.fetchall()}
    conn.close()
    return jsonify({
        'total_alerts': sum(severity_counts.values()),
        'by_severity': severity_counts,
        'by_category': category_counts
    })
