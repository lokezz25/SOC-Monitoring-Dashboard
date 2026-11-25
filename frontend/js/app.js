// app.js - Frontend logic for SOC Monitoring Dashboard
// Base API URL (same origin)
const API_BASE = '/api';

// Global data stores
let alertsData = [];
let agentsData = [];
let incidentsData = [];
let severityChart = null;
let categoryChart = null;

// ---------- Dashboard ----------
async function loadDashboard() {
    try {
        const res = await fetch(`${API_BASE}/alerts/statistics`);
        if (!res.ok) throw new Error(`Statistics API returned ${res.status}`);
        const data = await res.json();

        // KPI cards
        const total = data.total_alerts || 0;
        const totalEl = document.querySelector('#total-alerts .kpi-value');
        if (totalEl) totalEl.textContent = total;

        const sev = data.by_severity || {};
        const critEl = document.querySelector('#critical-alerts .kpi-value');
        if (critEl) critEl.textContent = sev['Critical'] || 0;

        const highEl = document.querySelector('#high-alerts .kpi-value');
        if (highEl) highEl.textContent = sev['High'] || 0;

        const medEl = document.querySelector('#medium-alerts .kpi-value');
        if (medEl) medEl.textContent = sev['Medium'] || 0;

        const lowEl = document.querySelector('#low-alerts .kpi-value');
        if (lowEl) lowEl.textContent = sev['Low'] || 0;

        // Incident counts
        try {
            const incRes = await fetch(`${API_BASE}/incidents`);
            if (incRes.ok) {
                const incData = await incRes.json();
                const active = incData.filter(i => i.status && i.status !== 'Resolved').length;
                const resolved = incData.filter(i => i.status === 'Resolved').length;
                const activeEl = document.querySelector('#active-incidents .kpi-value');
                if (activeEl) activeEl.textContent = active;
                const resEl = document.querySelector('#resolved-incidents .kpi-value');
                if (resEl) resEl.textContent = resolved;
            }
        } catch (e) {
            console.error('Failed to load incidents for KPI:', e);
        }

        // Agent online count
        try {
            const agRes = await fetch(`${API_BASE}/agents`);
            if (agRes.ok) {
                const agData = await agRes.json();
                const online = agData.filter(a => a.status === 'Online').length;
                const agEl = document.querySelector('#agents-status .kpi-value');
                if (agEl) agEl.textContent = online;
            }
        } catch (e) {
            console.error('Failed to load agents for KPI:', e);
        }

        // Charts
        const cat = data.by_category || {};
        const severities = Object.keys(sev);
        const severityCounts = severities.map(s => sev[s]);
        const categories = Object.keys(cat);
        const categoryCounts = categories.map(c => cat[c]);

        // Destroy previous charts before recreating
        if (severityChart) {
            severityChart.destroy();
            severityChart = null;
        }
        if (categoryChart) {
            categoryChart.destroy();
            categoryChart = null;
        }

        const sevCanvas = document.getElementById('severityChart');
        if (sevCanvas && typeof Chart !== 'undefined') {
            const ctxSev = sevCanvas.getContext('2d');
            severityChart = new Chart(ctxSev, {
                type: 'pie',
                data: {
                    labels: severities.length > 0 ? severities : ['No Data'],
                    datasets: [{
                        data: severityCounts.length > 0 ? severityCounts : [0],
                        backgroundColor: ['#ff4d4d', '#ff9900', '#ffdd00', '#66ff66', '#33ccff']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e0e4f1' } } }
                }
            });
        }

        const catCanvas = document.getElementById('categoryChart');
        if (catCanvas && typeof Chart !== 'undefined') {
            const ctxCat = catCanvas.getContext('2d');
            categoryChart = new Chart(ctxCat, {
                type: 'doughnut',
                data: {
                    labels: categories.length > 0 ? categories : ['No Data'],
                    datasets: [{
                        data: categoryCounts.length > 0 ? categoryCounts : [0],
                        backgroundColor: ['#8a2be2', '#00ced1', '#ff4500', '#3cb371', '#dda0dd', '#20b2aa']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e0e4f1' } } }
                }
            });
        }
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

// ---------- Alerts ----------
async function loadAlerts() {
    try {
        const res = await fetch(`${API_BASE}/alerts`);
        if (!res.ok) throw new Error(`Alerts API returned ${res.status}`);
        alertsData = await res.json();
        applyAlertFilters();
    } catch (err) {
        console.error('Failed to load alerts', err);
    }
}

function renderAlerts(data) {
    const tbody = document.getElementById('alerts-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.forEach(alert => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(alert.alert_id)}</td>
            <td>${escapeHtml(alert.timestamp)}</td>
            <td>${escapeHtml(alert.title)}</td>
            <td><span class="severity-badge sev-${(alert.severity || '').toLowerCase()}">${escapeHtml(alert.severity)}</span></td>
            <td>${escapeHtml(alert.category)}</td>
            <td>${escapeHtml(alert.status)}</td>
            <td>
                <button class="action-btn" data-id="${escapeHtml(alert.alert_id)}" data-action="view">View</button>
                <button class="action-btn" data-id="${escapeHtml(alert.alert_id)}" data-action="status">Status</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Attach Status update listeners
    tbody.querySelectorAll('.action-btn[data-action="status"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const alertId = btn.dataset.id;
            const newStatus = prompt('Enter new status (New, Investigating, Resolved):', 'Investigating');
            if (!newStatus) return;
            try {
                const resp = await fetch(`${API_BASE}/alerts/${encodeURIComponent(alertId)}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                if (resp.ok) {
                    alert('Status updated');
                    loadAlerts();
                    loadDashboard();
                } else {
                    alert('Failed to update status');
                }
            } catch (e) {
                console.error('Status update error:', e);
                alert('Error updating status');
            }
        });
    });

    // Attach View detail listeners
    tbody.querySelectorAll('.action-btn[data-action="view"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const alertId = btn.dataset.id;
            try {
                const resp = await fetch(`${API_BASE}/alerts/${encodeURIComponent(alertId)}`);
                if (resp.ok) {
                    const detail = await resp.json();
                    alert(`Alert Details:\nID: ${detail.alert_id}\nTitle: ${detail.title}\nDesc: ${detail.description || 'N/A'}\nSource IP: ${detail.src_ip || 'N/A'}\nDest IP: ${detail.dst_ip || 'N/A'}\nSeverity: ${detail.severity}\nCategory: ${detail.category}\nMITRE: ${detail.mitre_technique || 'N/A'}\nStatus: ${detail.status}\n\n[DEMO / SIMULATED DATA]`);
                } else {
                    alert('Alert not found');
                }
            } catch (e) {
                console.error('View detail error:', e);
            }
        });
    });
}

function applyAlertFilters() {
    const searchEl = document.getElementById('search-input');
    const sevEl = document.getElementById('severity-filter');
    const statEl = document.getElementById('status-filter');

    const term = searchEl ? searchEl.value.toLowerCase().trim() : '';
    const sev = sevEl ? sevEl.value : '';
    const stat = statEl ? statEl.value : '';

    const filtered = alertsData.filter(a => {
        const titleMatch = (a.title || '').toLowerCase().includes(term);
        const idMatch = (a.alert_id || '').toLowerCase().includes(term);
        const matchesTerm = !term || titleMatch || idMatch;
        const matchesSev = !sev || a.severity === sev;
        const matchesStat = !stat || a.status === stat;
        return matchesTerm && matchesSev && matchesStat;
    });
    renderAlerts(filtered);
}

// ---------- Agents ----------
async function loadAgents() {
    try {
        const res = await fetch(`${API_BASE}/agents`);
        if (!res.ok) throw new Error(`Agents API returned ${res.status}`);
        agentsData = await res.json();
        applyAgentFilters();
    } catch (err) {
        console.error('Failed to load agents', err);
    }
}

function renderAgents(data) {
    const tbody = document.getElementById('agents-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.forEach(agent => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(agent.agent_name)}</td>
            <td>${escapeHtml(agent.agent_id)}</td>
            <td>${escapeHtml(agent.hostname)}</td>
            <td>${escapeHtml(agent.os)}</td>
            <td>${escapeHtml(agent.ip_address)}</td>
            <td><span class="status-badge status-${(agent.status || '').toLowerCase()}">${escapeHtml(agent.status)}</span></td>
            <td>${escapeHtml(agent.last_activity)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function applyAgentFilters() {
    const searchEl = document.getElementById('agent-search');
    const statEl = document.getElementById('agent-status-filter');

    const term = searchEl ? searchEl.value.toLowerCase().trim() : '';
    const status = statEl ? statEl.value : '';

    const filtered = agentsData.filter(a => {
        const nameMatch = (a.agent_name || '').toLowerCase().includes(term);
        const idMatch = (a.agent_id || '').toLowerCase().includes(term);
        const matchesTerm = !term || nameMatch || idMatch;
        const matchesStatus = !status || a.status === status;
        return matchesTerm && matchesStatus;
    });
    renderAgents(filtered);
}

// ---------- Incidents ----------
async function loadIncidents() {
    try {
        const res = await fetch(`${API_BASE}/incidents`);
        if (!res.ok) throw new Error(`Incidents API returned ${res.status}`);
        incidentsData = await res.json();
        applyIncidentFilters();
    } catch (err) {
        console.error('Failed to load incidents', err);
    }
}

function renderIncidents(data) {
    const tbody = document.getElementById('incidents-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.forEach(inc => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(inc.incident_id)}</td>
            <td>${escapeHtml(inc.title)}</td>
            <td><span class="severity-badge sev-${(inc.severity || '').toLowerCase()}">${escapeHtml(inc.severity)}</span></td>
            <td>${escapeHtml(inc.assigned_analyst)}</td>
            <td>${escapeHtml(inc.status)}</td>
            <td>${escapeHtml(inc.created_at)}</td>
            <td><button class="action-btn" data-id="${escapeHtml(inc.incident_id)}" data-current="${escapeHtml(inc.status || 'New')}" data-action="status">Status</button></td>
        `;
        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.action-btn[data-action="status"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const incId = btn.dataset.id;
            const newStatus = prompt('Enter new status (New, Investigating, Resolved):', btn.dataset.current || 'New');
            if (!newStatus) return;
            try {
                const resp = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incId)}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                if (resp.ok) {
                    alert('Incident status updated');
                    loadIncidents();
                    loadDashboard();
                } else {
                    alert('Failed to update incident');
                }
            } catch (e) {
                console.error('Incident status update error:', e);
                alert('Error updating incident status');
            }
        });
    });
}

function applyIncidentFilters() {
    const searchEl = document.getElementById('incident-search');
    const statEl = document.getElementById('incident-status-filter');
    const sevEl = document.getElementById('incident-severity-filter');

    const term = searchEl ? searchEl.value.toLowerCase().trim() : '';
    const status = statEl ? statEl.value : '';
    const severity = sevEl ? sevEl.value : '';

    const filtered = incidentsData.filter(i => {
        const titleMatch = (i.title || '').toLowerCase().includes(term);
        const idMatch = (i.incident_id || '').toLowerCase().includes(term);
        const matchesTerm = !term || titleMatch || idMatch;
        const matchesStatus = !status || i.status === status;
        const matchesSeverity = !severity || i.severity === severity;
        return matchesTerm && matchesStatus && matchesSeverity;
    });
    renderIncidents(filtered);
}

// ---------- MITRE ATT&CK ----------
async function loadMitre() {
    try {
        const res = await fetch(`${API_BASE}/mitre`);
        if (!res.ok) throw new Error(`MITRE API returned ${res.status}`);
        const techniques = await res.json();
        renderMitre(techniques);
    } catch (err) {
        console.error('Failed to load MITRE data', err);
    }
}

function renderMitre(techniques) {
    const tbody = document.getElementById('mitre-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    techniques.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${escapeHtml(t.technique_id)}</strong></td>
            <td>${escapeHtml(t.tactic)}</td>
            <td>${escapeHtml(t.technique)}</td>
            <td>${escapeHtml(t.category)}</td>
            <td>${escapeHtml(t.description)}</td>
            <td><button class="action-btn" data-tech="${escapeHtml(t.technique_id)}">View Alerts</button></td>
        `;
        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('button[data-tech]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const techId = btn.dataset.tech;
            try {
                const resp = await fetch(`${API_BASE}/mitre/alerts/${encodeURIComponent(techId)}`);
                if (resp.ok) {
                    const alerts = await resp.json();
                    let msg = `Alerts for ${techId} (DEMO):\n\n`;
                    if (alerts.length > 0) {
                        alerts.forEach(a => {
                            msg += `- [${a.alert_id}] ${a.title} (${a.severity}) at ${a.timestamp}\n`;
                        });
                    } else {
                        msg += 'No alerts recorded for this technique yet.';
                    }
                    alert(msg);
                } else {
                    alert('Failed to load alerts for technique');
                }
            } catch (e) {
                console.error('Error fetching MITRE alerts:', e);
            }
        });
    });
}

// ---------- Helper ----------
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ---------- Initialization ----------
function initApp() {
    // 1. Navigation handling
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;

            // Active link styling
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show/hide sections
            document.querySelectorAll('.section').forEach(sec => {
                const shouldShow = sec.id === `${section}-section`;
                sec.classList.toggle('hidden', !shouldShow);
            });

            // Update header title
            const titleMap = {
                dashboard: 'Dashboard',
                alerts: 'Alerts',
                agents: 'Agents',
                incidents: 'Incidents',
                mitre: 'MITRE ATT&CK',
                reports: 'Reports'
            };
            const titleEl = document.getElementById('section-title');
            if (titleEl) titleEl.textContent = titleMap[section] || 'Dashboard';

            // Load data for the selected view
            if (section === 'dashboard') loadDashboard();
            else if (section === 'alerts') loadAlerts();
            else if (section === 'agents') loadAgents();
            else if (section === 'incidents') loadIncidents();
            else if (section === 'mitre') loadMitre();
        });
    });

    // 2. Alert filters
    const searchInput = document.getElementById('search-input');
    const severityFilter = document.getElementById('severity-filter');
    const statusFilter = document.getElementById('status-filter');
    if (searchInput) searchInput.addEventListener('input', applyAlertFilters);
    if (severityFilter) severityFilter.addEventListener('change', applyAlertFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyAlertFilters);

    // 3. Simulation panel buttons
    document.querySelectorAll('.sim-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const scenario = btn.dataset.scenario;
            btn.disabled = true;
            try {
                const res = await fetch(`${API_BASE}/simulation/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ scenario, count: 1 })
                });
                if (res.ok) {
                    const data = await res.json();
                    const gen = (data.generated && data.generated[0]) || {};
                    alert(`Simulated Alert Generated:\n[${gen.alert_id || 'ALERT'}] ${gen.title || scenario} (${gen.severity || 'Medium'})\n\n(DEMO/SIMULATED DATA)`);
                    loadDashboard();
                    const alertsSec = document.getElementById('alerts-section');
                    if (alertsSec && !alertsSec.classList.contains('hidden')) {
                        loadAlerts();
                    }
                } else {
                    const err = await res.json().catch(() => ({}));
                    alert('Error: ' + (err.error || `HTTP ${res.status}`));
                }
            } catch (e) {
                console.error('Simulation request failed', e);
                alert('Failed to connect to simulation API');
            } finally {
                btn.disabled = false;
            }
        });
    });

    // 4. Clear demo alerts button
    const clearBtn = document.getElementById('clear-demo');
    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (!confirm('Delete all DEMO alerts?')) return;
            clearBtn.disabled = true;
            try {
                const res = await fetch(`${API_BASE}/simulation/clear`, { method: 'POST' });
                if (res.ok) {
                    alert('Demo alerts cleared successfully.');
                    loadDashboard();
                    const alertsSec = document.getElementById('alerts-section');
                    if (alertsSec && !alertsSec.classList.contains('hidden')) {
                        loadAlerts();
                    }
                } else {
                    const err = await res.json().catch(() => ({}));
                    alert('Error clearing alerts: ' + (err.error || `HTTP ${res.status}`));
                }
            } catch (e) {
                console.error('Clear alerts request failed', e);
                alert('Failed to clear demo alerts');
            } finally {
                clearBtn.disabled = false;
            }
        });
    }

    // 5. Agent filters
    const agentSearch = document.getElementById('agent-search');
    const agentStatus = document.getElementById('agent-status-filter');
    if (agentSearch) agentSearch.addEventListener('input', applyAgentFilters);
    if (agentStatus) agentStatus.addEventListener('change', applyAgentFilters);

    // 6. Incident filters
    const incidentSearch = document.getElementById('incident-search');
    const incidentStatus = document.getElementById('incident-status-filter');
    const incidentSeverity = document.getElementById('incident-severity-filter');
    if (incidentSearch) incidentSearch.addEventListener('input', applyIncidentFilters);
    if (incidentStatus) incidentStatus.addEventListener('change', applyIncidentFilters);
    if (incidentSeverity) incidentSeverity.addEventListener('change', applyIncidentFilters);

    // 7. PDF report generation
    const reportBtn = document.getElementById('generate-report');
    if (reportBtn) {
        reportBtn.addEventListener('click', async () => {
            const startInput = document.getElementById('report-start');
            const endInput = document.getElementById('report-end');
            const start = startInput ? startInput.value : '';
            const end = endInput ? endInput.value : '';
            const payload = {};
            if (start) payload.start_date = start;
            if (end) payload.end_date = end;

            reportBtn.disabled = true;
            reportBtn.textContent = 'Generating...';
            try {
                const res = await fetch(`${API_BASE}/reports/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `SOC_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                } else {
                    const err = await res.json().catch(() => ({}));
                    alert('Report generation failed: ' + (err.error || `HTTP ${res.status}`));
                }
            } catch (e) {
                console.error('Report request failed', e);
                alert('Failed to generate report');
            } finally {
                reportBtn.disabled = false;
                reportBtn.textContent = 'Download PDF';
            }
        });
    }

    // 8. Initial dashboard load
    loadDashboard();
}

// Ensure execution once DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
