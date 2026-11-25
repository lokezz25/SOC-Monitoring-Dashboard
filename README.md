
# SOC Monitoring Dashboard

## Overview
A premium‑grade Security Operations Center (SOC) monitoring dashboard built **entirely as a self‑contained simulation**. It showcases realistic security alerts, incident management, agent monitoring, MITRE ATT&CK mapping, and PDF report generation – all without any external SIEM (e.g., Wazuh).

- **Frontend** – HTML5 / CSS3 / JavaScript with Chart.js, glass‑morphism UI, dark midnight‑navy theme.
- **Backend** – Python Flask REST API, SQLite persistence.
- **Simulation Engine** – Generates demo alerts for common attack scenarios.
- **PDF Reports** – Export alert‑summary PDFs via ReportLab.

All data is **demo/simulated** and clearly labeled as such.

## Project Structure
```
SOC-Monitoring-Dashboard/
├─ backend/
│   ├─ app.py                     # Flask entry point
│   ├─ requirements.txt            # Python deps
│   ├─ database/
│   │   └─ __init__.py            # DB schema & seed data
│   └─ routes/
│       ├─ __init__.py            # (empty – makes package)
│       ├─ alerts.py               # Alert CRUD & stats
│       ├─ incidents.py            # Incident CRUD
│       ├─ agents.py               # Agent read‑only API
│       ├─ reports.py              # PDF generation
│       └─ simulation.py           # Alert generation engine
├─ frontend/
│   ├─ index.html                 # Main UI
│   ├─ css/
│   │   └─ style.css              # Dark glass‑morphism theme
│   └─ js/
│       └─ app.js                 # UI logic, API calls
└─ README.md                      # This file
```

## Prerequisites (Windows)
- **PowerShell 5+** (default on Windows 10/11)
- **Python 3.11+** (download from https://www.python.org/)
- **Git** (optional, for cloning the repo)

## Setup & Installation
1. **Open PowerShell** and navigate to where you want the project:
   ```powershell
   cd $HOME
   # optional: clone if you have a repo URL
   # git clone <repo-url>
   ```
2. **Create the project folder** (if not already present):
   ```powershell
   New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.gemini\antigravity\scratch\SOC-Monitoring-Dashboard" -Force
   ```
3. **Copy the source files** into that folder (the agent already placed them under the `scratch` directory).
4. **Create a virtual environment** (highly recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
5. **Install dependencies**:
   ```powershell
   pip install -r backend\requirements.txt
   ```
6. **Initialize the SQLite database** (executed automatically on first run, but you can run manually):
   ```powershell
   python -c "import backend.database as db; db.init_db()"
   ```
7. **Start the Flask development server**:
   ```powershell
   python backend\app.py
   ```
   The server will listen on **http://0.0.0.0:5000**.
8. **Open the dashboard** in a browser:
   ```powershell
   start http://localhost:5000
   ```
   You should see the dark SOC UI.

## Usage
- **Dashboard** – shows KPI cards, severity & category pie charts.
- **Simulation Panel** – click any button to generate a single demo alert for that scenario. Use *Clear Demo Alerts* to wipe the generated data.
- **Alerts page** – view, search, filter, and update alert status (New / Investigating / Resolved).
- **PDF Report** – select a date range (optional) and click *Download PDF*; the report includes a header, alert counts, severity/category breakdown, and a table of alerts (all marked **DEMO/SIMULATED**).

All buttons are fully wired to the Flask back‑end; no placeholder pages remain.

## Testing
You can verify the API endpoints with `curl` (or PowerShell `Invoke-RestMethod`). Example:
```powershell
# List alerts
Invoke-RestMethod http://localhost:5000/api/alerts

# Generate a brute‑force alert
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/simulation/generate -Body '{"scenario":"brute_force","count":1}' -ContentType 'application/json'
```
The UI automatically refreshes after actions.

## Extending the Project
- Add more **MITRE ATT&CK** pages by creating a new route and UI section.
- Implement **incident‑to‑alert linking** (store `alert_id` in the incident table).
- Replace the basic PDF layout with a richer design using ReportLab's drawing primitives.

## License
MIT – feel free to adapt for academic demos or commercial prototypes.

---
**Enjoy your premium SOC monitoring demo!**

# SOC-Monitoring-Dashboard
A Security operations center monitoring dashboard using Python flask

