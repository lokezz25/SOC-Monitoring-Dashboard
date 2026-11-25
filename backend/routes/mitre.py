from flask import Blueprint, jsonify
import sqlite3

mitre_bp = Blueprint('mitre', __name__)

def get_db():
    from database import get_connection
    return get_connection()

# Static MITRE ATT&CK data (demo only)
MITRE_DATA = [
    {
        "technique_id": "T1110",
        "tactic": "Credential Access",
        "technique": "Brute Force",
        "category": "Authentication",
        "description": "Attempts to guess passwords by trying many combinations."
    },
    {
        "technique_id": "T1046",
        "tactic": "Reconnaissance",
        "technique": "Network Service Scanning",
        "category": "Reconnaissance",
        "description": "Scanning of ports and services on target hosts."
    },
    {
        "technique_id": "T1059",
        "tactic": "Execution",
        "technique": "Command and Scripting Interpreter",
        "category": "Malware",
        "description": "Malicious scripts executed on host."
    },
    {
        "technique_id": "T1190",
        "tactic": "Initial Access",
        "technique": "Exploit Public-Facing Application",
        "category": "Injection",
        "description": "SQL injection attempts against web apps."
    },
    {
        "technique_id": "T1068",
        "tactic": "Privilege Escalation",
        "technique": "Exploitation for Privilege Escalation",
        "category": "Privilege Escalation",
        "description": "Gaining higher privileges on a system."
    },
    {
        "technique_id": "T1041",
        "tactic": "Exfiltration",
        "technique": "Exfiltration Over Command and Control Channel",
        "category": "Exfiltration",
        "description": "Suspicious data transfers out of the network."
    }
]

@mitre_bp.route('', methods=['GET'])
@mitre_bp.route('/', methods=['GET'])
def list_mitre():
    return jsonify(MITRE_DATA)

@mitre_bp.route('/alerts/<technique_id>', methods=['GET'])
def alerts_by_technique(technique_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM alerts WHERE mitre_technique = ?', (technique_id,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)
