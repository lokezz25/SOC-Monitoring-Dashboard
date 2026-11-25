from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

incidents_bp = Blueprint('incidents', __name__)

def get_db():
    from database import get_connection
    return get_connection()

@incidents_bp.route('', methods=['GET'])
@incidents_bp.route('/', methods=['GET'])
def list_incidents():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM incidents')
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@incidents_bp.route('/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM incidents WHERE incident_id = ?', (incident_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error':'Incident not found'}),404

@incidents_bp.route('', methods=['POST'])
@incidents_bp.route('/', methods=['POST'])
def create_incident():
    data = request.json or {}
    required = ['incident_id','title','severity','assigned_analyst','status','created_at']
    if not all(k in data for k in required):
        return jsonify({'error':'Missing fields'}),400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO incidents (incident_id,title,severity,assigned_analyst,status,resolution_time,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)''',
                (data['incident_id'], data['title'], data['severity'], data['assigned_analyst'], data['status'], data.get('resolution_time'), data['created_at'], data.get('updated_at')))
    conn.commit()
    conn.close()
    return jsonify({'message':'Incident created'}),201

@incidents_bp.route('/<incident_id>/status', methods=['PUT'])
def update_incident_status(incident_id):
    data = request.json or {}
    status = data.get('status')
    if not status:
        return jsonify({'error':'Missing status'}),400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE incidents SET status = ?, updated_at = ? WHERE incident_id = ?', (status, datetime.utcnow().isoformat(), incident_id))
    conn.commit()
    conn.close()
    return jsonify({'message':'Status updated'})

@incidents_bp.route('/<incident_id>/notes', methods=['POST'])
def add_note(incident_id):
    data = request.json or {}
    note = data.get('note')
    if not note:
        return jsonify({'error':'Missing note'}),400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO notes (incident_id, note, created_at) VALUES (?,?,?)',
                (incident_id, note, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'message':'Note added'}),201
