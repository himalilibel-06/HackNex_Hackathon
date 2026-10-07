"""
SAFE SIGHT - Automatic Incident Report Generator Module (core/report.py)

This module exports master JSON incident records, dashboard summary metrics,
and auto-generates clean, professional HTML incident reports containing risk scores,
itemized reasons, activity sequences, and evidence snapshots.
"""

import os
import json
from typing import List, Dict, Any


class ReportGenerator:
    """
    Generates structured JSON data and HTML incident reports.
    """
    @staticmethod
    def export_summary(summary_data: Dict[str, Any], output_path: str = "output/reports/summary.json"):
        """Export dashboard-ready summary metrics to JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

    @staticmethod
    def export_incidents_json(incidents: List[Dict[str, Any]], master_path: str = "output/reports/incidents.json"):
        """Export master incidents list to JSON."""
        os.makedirs(os.path.dirname(master_path), exist_ok=True)
        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(incidents, f, indent=2)

        # Also write per-incident JSON files
        reports_dir = os.path.dirname(master_path)
        for inc in incidents:
            inc_file = os.path.join(reports_dir, f"incident_{inc['incident_id']}.json")
            with open(inc_file, "w", encoding="utf-8") as f:
                json.dump(inc, f, indent=2)

    @staticmethod
    def generate_html_report(incident: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a clean HTML incident report file.

        Parameters:
            incident (Dict[str, Any]): Incident dictionary record.
            output_path (str): File path to save HTML report.

        Returns:
            str: Path to saved HTML report.
        """
        inc_id = incident["incident_id"]
        if output_path is None:
            output_path = f"output/reports/incident_{inc_id}.html"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        reasons_html = "".join([f"<li>{r}</li>" for r in incident.get("risk_reasons", [])])
        evidence_html = "".join([f"<img src='../../{ev}' style='max-width:320px; margin:8px; border-radius:6px; border:2px solid #333;' alt='Evidence'/>" for ev in incident.get("evidence", []) if ev])

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SAFE SIGHT - Incident Report {inc_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 24px; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; margin-top: 0; border-bottom: 2px solid #334155; padding-bottom: 12px; }}
        .badge-critical {{ background: #ef4444; color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
        .badge-high {{ background: #f97316; color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; background: #0f172a; padding: 16px; border-radius: 8px; }}
        .meta-item {{ font-size: 14px; color: #94a3b8; }}
        .meta-value {{ font-weight: bold; color: #f8fafc; font-size: 16px; margin-top: 4px; }}
        ul {{ color: #cbd5e1; line-height: 1.6; }}
        .evidence-box {{ margin-top: 20px; background: #0f172a; padding: 16px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ SAFE SIGHT INCIDENT REPORT</h1>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>Incident ID: {inc_id}</h2>
            <span class="badge-{incident['risk_level'].lower()}">{incident['risk_level']} RISK ({incident['risk_score']}/100)</span>
        </div>

        <div class="meta-grid">
            <div class="meta-item">Person Track ID<div class="meta-value">{incident['track_id']}</div></div>
            <div class="meta-item">Location / Zone<div class="meta-value">{incident['zone']}</div></div>
            <div class="meta-item">Simulated CCTV Time<div class="meta-value">{incident['cctv_time']}</div></div>
            <div class="meta-item">Timestamp Range<div class="meta-value">{incident['start_time']:.1f}s - {incident['end_time']:.1f}s</div></div>
            <div class="meta-item">Primary Behaviour<div class="meta-value">{incident['behaviour'].capitalize()}</div></div>
            <div class="meta-item">Status<div class="meta-value">{incident['status']}</div></div>
        </div>

        <h3>📌 Explanation</h3>
        <p style="background: #0f172a; padding: 12px; border-left: 4px solid #38bdf8; border-radius: 4px; color: #e2e8f0;">
            {incident['explanation']}
        </p>

        <h3>⚠️ Itemized Risk Reasons</h3>
        <ul>{reasons_html}</ul>

        <div class="evidence-box">
            <h3>📷 Evidence Snapshots</h3>
            <div>{evidence_html if evidence_html else "<p>No snapshots attached.</p>"}</div>
        </div>
    </div>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path
