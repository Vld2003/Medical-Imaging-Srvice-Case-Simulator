from __future__ import annotations
from datetime import datetime
from html import escape
from typing import Dict, List
def build_html_report(file_name: str,metadata: Dict[str, str],metrics: Dict[str, float],status: str,observations: List[str],recommendations: List[str],) -> str:
  #Build a simple HTML QA-style report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    metric_rows = "\n".join(f"<tr><td>{escape(key)}</td><td>{value:.3f}</td></tr>"for key, value in metrics.items())
    metadata_rows = "\n".join(f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>"for key, value in metadata.items())
    obs_items = "\n".join(f"<li>{escape(item)}</li>" for item in observations)
    rec_items = "\n".join(f"<li>{escape(item)}</li>" for item in recommendations)
    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <title>Medical Imaging QA Report</title>
    <style>
        body {{font-family: Arial, sans-serif;margin: 40px;line-height: 1.5;color: #222;}}
        h1, h2 {{color: #1f4e79;}}
        table {{border-collapse: collapse;width: 100%;margin-bottom: 24px;}}
        th, td {{border: 1px solid #bbb;padding: 8px;text-align: left;}}
        th {{background: #e8f1fa;}}
        .status {{padding: 12px;background: #f5f5f5;border-left: 5px solid #1f4e79; font-weight: bold;}}
        .disclaimer {{margin-top: 32px;padding: 12px;background: #fff4e5;border-left: 5px solid #d9822b;}}
    </style>
</head>
<body>
    <h1>Medical Imaging QA-style Technical Report</h1>
    <p><strong>Generated:</strong> {escape(now)}</p>
    <p><strong>File / Case:</strong> {escape(file_name)}</p>
    <div class="status">Status: {escape(status)}</div>
    <h2>Metadata</h2>
    <table>
        <tr><th>Field</th><th>Value</th></tr>
        {metadata_rows}
    </table>
    <h2>Calculated Metrics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        {metric_rows}
    </table>
    <h2>Technical Observations</h2>
    <ul>
        {obs_items}
    </ul>
    <h2>Recommended Checks</h2>
    <ul>
        {rec_items}
    </ul>
    <div class="disclaimer">
        <strong>Disclaimer:</strong> This report is educational and portfolio-oriented.
        It is not a validated medical device, not a diagnostic tool, and must not be used for clinical decisions.
    </div>
</body>
</html>
"""
