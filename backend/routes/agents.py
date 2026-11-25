from flask import Blueprint, jsonify
import sqlite3

agents_bp = Blueprint('agents', __name__)

def get_db():
    from database import get_connection
    return get_connection()

@agents_bp.route('', methods=['GET'])
@agents_bp.route('/', methods=['GET'])
def list_agents():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM agents')
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM agents WHERE agent_id = ?', (agent_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error':'Agent not found'}), 404
