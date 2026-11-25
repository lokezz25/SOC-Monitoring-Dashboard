from flask import Blueprint, request, jsonify, current_app, send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

def get_db():
    from database import get_connection
    return get_connection()

@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    data = request.json or {}
    start_date = data.get('start_date')  # ISO format string or None
    end_date = data.get('end_date')
    conn = get_db()
    cur = conn.cursor()
    # Filter alerts by date if provided
    query = 'SELECT * FROM alerts'
    params = []
    if start_date and end_date:
        query += ' WHERE timestamp BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    cur.execute(query, params)
    alerts = [dict(row) for row in cur.fetchall()]
    # Gather statistics
    cur.execute('SELECT severity, COUNT(*) as cnt FROM alerts GROUP BY severity')
    severity_stats = {row['severity']: row['cnt'] for row in cur.fetchall()}
    cur.execute('SELECT category, COUNT(*) as cnt FROM alerts GROUP BY category')
    category_stats = {row['category']: row['cnt'] for row in cur.fetchall()}
    # Simple PDF generation
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    p.setFont('Helvetica-Bold', 16)
    p.drawString(50, y, 'SOC Monitoring Dashboard Report')
    y -= 30
    p.setFont('Helvetica', 12)
    p.drawString(50, y, f'Generated on: {datetime.utcnow().isoformat()} UTC')
    y -= 20
    p.drawString(50, y, f'Date range: {start_date or "All"} to {end_date or "Now"}')
    y -= 30
    p.drawString(50, y, f'Total Alerts: {len(alerts)}')
    y -= 20
    p.drawString(50, y, 'Alerts by Severity:')
    for sev, cnt in severity_stats.items():
        y -= 15
        p.drawString(70, y, f'{sev}: {cnt}')
    y -= 20
    p.drawString(50, y, 'Alerts by Category:')
    for cat, cnt in category_stats.items():
        y -= 15
        p.drawString(70, y, f'{cat}: {cnt}')
    y -= 30
    p.drawString(50, y, 'Alert Details (Demo/SIMULATED):')
    y -= 20
    p.setFont('Helvetica', 9)
    for alert in alerts:
        if y < 60:
            p.showPage()
            y = height - 50
        line = f"{alert['timestamp']} | {alert['severity']} | {alert['title']} | Src:{alert['src_ip']} Dst:{alert['dst_ip']}"
        p.drawString(50, y, line)
        y -= 12
    p.showPage()
    p.save()
    buffer.seek(0)
    conn.close()
    return send_file(buffer, as_attachment=True, download_name='SOC_Report.pdf', mimetype='application/pdf')
