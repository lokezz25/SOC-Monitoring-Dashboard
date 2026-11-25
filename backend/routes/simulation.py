from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
import uuid
import sqlite3

simulation_bp = Blueprint('simulation', __name__)

def get_db():
    from database import get_connection
    return get_connection()

# Helper to insert alert
def insert_alert(conn, alert):
    cur = conn.cursor()
    cur.execute('''INSERT INTO alerts (alert_id, timestamp, title, description, src_ip, dst_ip, severity, category, mitre_technique, status)
                   VALUES (?,?,?,?,?,?,?,?,?,?)''', (
        alert['alert_id'],
        alert['timestamp'],
        alert['title'],
        alert.get('description', ''),
        alert.get('src_ip', ''),
        alert.get('dst_ip', ''),
        alert['severity'],
        alert['category'],
        alert.get('mitre_technique', ''),
        alert.get('status', 'New')
    ))
    conn.commit()

# Simple IP generator
def random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

# Scenario implementations
def generate_failed_login():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Failed Login Attempt',
        'description': 'User provided wrong credentials',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'Low',
        'category': 'Authentication',
        'mitre_technique': 'T1110',
        'status': 'New'
    }

def generate_brute_force():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Brute Force Login Attempt',
        'description': 'Multiple rapid login attempts detected',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'High',
        'category': 'Authentication',
        'mitre_technique': 'T1110',
        'status': 'New'
    }

def generate_port_scan():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Port Scan Detected',
        'description': 'Scanning multiple ports on internal host',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'Medium',
        'category': 'Reconnaissance',
        'mitre_technique': 'T1046',
        'status': 'New'
    }

def generate_malware():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Malware Detection',
        'description': 'Known malicious hash observed in file',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'Critical',
        'category': 'Malware',
        'mitre_technique': 'T1059',
        'status': 'New'
    }

def generate_sql_injection():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'SQL Injection Attempt',
        'description': 'Suspicious query patterns detected',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'High',
        'category': 'Injection',
        'mitre_technique': 'T1190',
        'status': 'New'
    }

def generate_privilege_escalation():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Privilege Escalation',
        'description': 'Process gained higher privileges unexpectedly',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'Critical',
        'category': 'Privilege Escalation',
        'mitre_technique': 'T1068',
        'status': 'New'
    }

def generate_network_traffic():
    return {
        'alert_id': f'ALERT-{uuid.uuid4().hex[:6].upper()}',
        'timestamp': datetime.utcnow().isoformat(),
        'title': 'Suspicious Network Traffic',
        'description': 'Unusual data transfer volume observed',
        'src_ip': random_ip(),
        'dst_ip': random_ip(),
        'severity': 'Medium',
        'category': 'Exfiltration',
        'mitre_technique': 'T1041',
        'status': 'New'
    }

SCENARIOS = {
    'failed_login': generate_failed_login,
    'brute_force': generate_brute_force,
    'port_scan': generate_port_scan,
    'malware': generate_malware,
    'sql_injection': generate_sql_injection,
    'privilege_escalation': generate_privilege_escalation,
    'network_traffic': generate_network_traffic,
}

@simulation_bp.route('/generate', methods=['POST'])
@simulation_bp.route('/generate/', methods=['POST'])
def generate_alerts():
    data = request.get_json(force=True, silent=True) or {}
    scenario = data.get('scenario')
    try:
        count = int(data.get('count', 1))
    except (ValueError, TypeError):
        count = 1
    if not scenario or scenario not in SCENARIOS:
        return jsonify({'error': f'Invalid scenario: {scenario}'}), 400
    conn = get_db()
    alerts = []
    for _ in range(count):
        alert = SCENARIOS[scenario]()
        insert_alert(conn, alert)
        alerts.append(alert)
    conn.close()
    return jsonify({'generated': alerts}), 200

@simulation_bp.route('/clear', methods=['POST'])
@simulation_bp.route('/clear/', methods=['POST'])
def clear_demo():
    conn = get_db()
    cur = conn.cursor()
    # Remove only DEMO alerts – we tag by alert_id prefix "ALERT-"
    cur.execute("DELETE FROM alerts WHERE alert_id LIKE 'ALERT-%'")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Demo alerts cleared'}), 200
