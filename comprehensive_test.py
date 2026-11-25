import sys, os, json
BASE_DIR = r'C:\Users\lokna\.gemini\antigravity\scratch\SOC-Monitoring-Dashboard'
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from app import app

client = app.test_client()

results = []

def test(name, fn):
    try:
        fn()
        results.append((name, "PASS", ""))
    except Exception as e:
        results.append((name, "FAIL", str(e)))

# 1. Static files
def test_static():
    r = client.get('/')
    assert r.status_code == 200, f"Status {r.status_code}"
    assert b'SOC Dashboard' in r.data
    r_css = client.get('/css/style.css')
    assert r_css.status_code == 200
    r_js = client.get('/js/app.js')
    assert r_js.status_code == 200

test("Static Files (index.html, style.css, app.js)", test_static)

# 2. Simulation endpoints
def test_simulation():
    scenarios = ['failed_login', 'brute_force', 'port_scan', 'malware', 'sql_injection', 'privilege_escalation', 'network_traffic']
    for sc in scenarios:
        r = client.post('/api/simulation/generate', json={'scenario': sc, 'count': 1})
        assert r.status_code == 200, f"Scenario {sc} returned {r.status_code}: {r.get_data(as_text=True)}"
        data = json.loads(r.get_data(as_text=True))
        assert 'generated' in data
        assert len(data['generated']) == 1
        assert data['generated'][0]['category'] is not None

    # Invalid scenario
    r = client.post('/api/simulation/generate', json={'scenario': 'non_existent', 'count': 1})
    assert r.status_code == 400

    # Clear demo alerts
    r = client.post('/api/simulation/clear')
    assert r.status_code == 200, f"Clear returned {r.status_code}"

test("Simulation Generate (All 7 Scenarios) & Clear", test_simulation)

# 3. Alerts endpoints
def test_alerts():
    # Generate an alert first
    client.post('/api/simulation/generate', json={'scenario': 'brute_force', 'count': 1})
    r = client.get('/api/alerts/')
    assert r.status_code == 200
    alerts = json.loads(r.get_data(as_text=True))
    assert len(alerts) > 0
    alert_id = alerts[0]['alert_id']

    # Get single alert
    r_single = client.get(f'/api/alerts/{alert_id}')
    assert r_single.status_code == 200

    # Update status
    r_put = client.put(f'/api/alerts/{alert_id}/status', json={'status': 'Investigating'})
    assert r_put.status_code == 200

    # Statistics
    r_stats = client.get('/api/alerts/statistics')
    assert r_stats.status_code == 200
    stats = json.loads(r_stats.get_data(as_text=True))
    assert 'total_alerts' in stats
    assert 'by_severity' in stats
    assert 'by_category' in stats

test("Alerts CRUD & Statistics", test_alerts)

# 4. Incidents endpoints
def test_incidents():
    r = client.get('/api/incidents/')
    assert r.status_code == 200

    # Create an incident if none
    incidents = json.loads(r.get_data(as_text=True))
    if not incidents:
        client.post('/api/incidents/', json={
            'incident_id': 'INC-001',
            'title': 'Test Incident',
            'severity': 'High',
            'assigned_analyst': 'Analyst 1',
            'status': 'New',
            'created_at': '2026-11-23T08:00:00'
        })
        r = client.get('/api/incidents/')
        incidents = json.loads(r.get_data(as_text=True))

    inc_id = incidents[0]['incident_id']
    r_put = client.put(f'/api/incidents/{inc_id}/status', json={'status': 'Investigating'})
    assert r_put.status_code == 200

    r_note = client.post(f'/api/incidents/{inc_id}/notes', json={'note': 'Test investigation note'})
    assert r_note.status_code == 201

test("Incidents Management & Notes", test_incidents)

# 5. Agents endpoints
def test_agents():
    r = client.get('/api/agents/')
    assert r.status_code == 200
    agents = json.loads(r.get_data(as_text=True))
    assert len(agents) > 0

test("Agents List", test_agents)

# 6. MITRE endpoints
def test_mitre():
    r = client.get('/api/mitre/')
    assert r.status_code == 200
    mitre_data = json.loads(r.get_data(as_text=True))
    assert len(mitre_data) > 0
    t_id = mitre_data[0]['technique_id']
    r_alerts = client.get(f'/api/mitre/alerts/{t_id}')
    assert r_alerts.status_code == 200

test("MITRE ATT&CK Mapping & Alerts", test_mitre)

# 7. PDF Report Generation
def test_reports():
    r = client.post('/api/reports/generate', json={})
    assert r.status_code == 200
    assert r.content_type == 'application/pdf'
    assert len(r.data) > 500
    assert r.data[:4] == b'%PDF'

test("PDF Report Generation", test_reports)

print("\n--- TEST RESULTS ---")
all_passed = True
for name, status, err in results:
    print(f"[{status}] {name}" + (f" - Error: {err}" if err else ""))
    if status != "PASS":
        all_passed = False

if all_passed:
    print("\nALL 7 TEST SUITES PASSED PERFECTLY!")
else:
    sys.exit(1)
