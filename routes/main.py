from flask import Blueprint, render_template, make_response
import os

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'index.html'), 'r') as f:
        content = f.read()
    response = make_response(content)
    response.headers["Content-Type"] = "text/html"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@main_bp.route("/reset-password")
def reset_password():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'index.html'), 'r') as f:
        content = f.read()
    response = make_response(content)
    response.headers["Content-Type"] = "text/html"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@main_bp.route("/invite")
def invite():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'invite.html')
    with open(path, 'r') as f:
        html = f.read()
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response

@main_bp.route("/admin/users")
def admin_users():
    from flask import request
    from models import User, Protocol, DoseLog
    from datetime import date, timedelta
    key = request.args.get("key", "")
    if key != "mg42admin2024":
        return "Unauthorized", 403

    with __import__('flask').current_app.app_context():
        patients = User.query.filter_by(role="patient").order_by(User.created_at.desc()).all()

    rows = ""
    for u in patients:
        protocol_count = Protocol.query.filter_by(patient_id=u.id).count()
        last_dose = DoseLog.query.filter_by(patient_id=u.id).order_by(DoseLog.created_at.desc()).first()
        last_dose_str = last_dose.date.strftime("%b %d") if last_dose else "never"
        rows += f"""
        <tr>
          <td>{u.created_at.strftime("%b %d, %Y") if u.created_at else "—"}</td>
          <td>{u.first_name or ""} {u.last_name or ""}</td>
          <td style="font-family:monospace">{u.username}</td>
          <td>{u.email or "—"}</td>
          <td style="text-align:center">{protocol_count}</td>
          <td style="text-align:center">{last_dose_str}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>PeptideTrack Users</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #080f1a; color: #e8f4f8; padding: 20px; font-size: 14px; }}
    h1 {{ font-size: 18px; color: #00d4c8; margin-bottom: 4px; }}
    p {{ color: #5a8099; font-size: 12px; margin-bottom: 20px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: #5a8099; padding: 8px 10px; border-bottom: 1px solid #1a2d42; }}
    td {{ padding: 10px; border-bottom: 1px solid #1a2d42; font-size: 13px; vertical-align: top; }}
    tr:hover td {{ background: #0d1826; }}
    .count {{ font-family: monospace; font-size: 32px; font-weight: 700; color: #00d4c8; }}
  </style>
</head>
<body>
  <h1>💉 PeptideTrack</h1>
  <p>Registered patients</p>
  <div class="count">{len(patients)}</div>
  <p style="margin-top:4px">total accounts</p>
  <table>
    <thead>
      <tr>
        <th>Joined</th>
        <th>Name</th>
        <th>Username</th>
        <th>Email</th>
        <th>Protocols</th>
        <th>Last dose</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
    return html

@main_bp.route("/health")
def health():
    from flask import jsonify
    return jsonify({"status": "ok"}), 200
