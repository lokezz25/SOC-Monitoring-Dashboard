import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'soc_dashboard.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        src_ip TEXT,
        dst_ip TEXT,
        severity TEXT,
        category TEXT,
        mitre_technique TEXT,
        status TEXT DEFAULT 'New'
    )
    ''')
    # Incidents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT NOT NULL,
        title TEXT NOT NULL,
        severity TEXT,
        assigned_analyst TEXT,
        status TEXT,
        resolution_time TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    # Agents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT,
        agent_id TEXT,
        hostname TEXT,
        os TEXT,
        ip_address TEXT,
        status TEXT,
        last_activity TEXT
    )
    ''')
    # Investigation notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT,
        note TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    # Seed sample data if tables empty
    seed_sample_data(conn)
    conn.close()

def seed_sample_data(conn):
    cursor = conn.cursor()
    # Check if alerts already exist
    cursor.execute('SELECT COUNT(*) FROM alerts')
    if cursor.fetchone()[0] == 0:
        # Insert a few demo alerts
        demo_alerts = [
            ('ALERT-001', '2026-11-22 12:00:00', 'Failed Login Attempt', 'Multiple failed logins detected', '192.168.1.10', '10.0.0.5', 'Low', 'Authentication', 'T1110', 'New'),
            ('ALERT-002', '2026-11-22 13:15:22', 'Port Scan Detected', 'Port scanning activity from external IP', '203.0.113.45', '10.0.0.12', 'Medium', 'Reconnaissance', 'T1046', 'New'),
        ]
        cursor.executemany('INSERT INTO alerts (alert_id, timestamp, title, description, src_ip, dst_ip, severity, category, mitre_technique, status) VALUES (?,?,?,?,?,?,?,?,?,?)', demo_alerts)
    # Seed agents
    cursor.execute('SELECT COUNT(*) FROM agents')
    if cursor.fetchone()[0] == 0:
        demo_agents = [
            ('Demo Agent 1', 'AGENT-001', 'host1', 'Windows Server 2019', '10.0.0.5', 'Online', '2026-11-22 23:55:00'),
            ('Demo Agent 2', 'AGENT-002', 'host2', 'Ubuntu 22.04', '10.0.0.12', 'Online', '2026-11-22 23:58:00'),
        ]
        cursor.executemany('INSERT INTO agents (agent_name, agent_id, hostname, os, ip_address, status, last_activity) VALUES (?,?,?,?,?,?,?)', demo_agents)
    conn.commit()
