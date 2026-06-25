from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, CheckIn, DoseLog, Protocol
from datetime import date, datetime

patients_bp = Blueprint("patients", __name__)

def practitioner_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "practitioner":
            return jsonify({"error": "Practitioner access required"}), 403
        return f(*args, **kwargs)
    return decorated


@patients_bp.route("/", methods=["GET"])
@login_required
@practitioner_required
def get_all():
    patients = User.query.filter_by(practitioner_id=current_user.id, role="patient").order_by(User.first_name).all()
    result = []
    for p in patients:
        d = p.to_dict()
        # Add adherence and last check-in
        last_checkin = CheckIn.query.filter_by(patient_id=p.id).order_by(CheckIn.date.desc()).first()
        d["last_checkin"] = last_checkin.date.isoformat() if last_checkin else None
        d["last_weight"]  = last_checkin.weight_lbs if last_checkin else None
        active_protocol = Protocol.query.filter_by(patient_id=p.id, active=True).first()
        d["protocol_name"] = active_protocol.name if active_protocol else None
        result.append(d)
    return jsonify(result), 200


@patients_bp.route("/<int:patient_id>", methods=["GET"])
@login_required
def get_one(patient_id):
    patient = User.query.get_or_404(patient_id)
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(patient.to_dict()), 200


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
@login_required
def update(patient_id):
    patient = User.query.get_or_404(patient_id)
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    for field in ("first_name", "last_name", "goals", "notes"):
        if field in data:
            setattr(patient, field, data[field])
    if "weight_lbs" in data:
        patient.weight_lbs = float(data["weight_lbs"]) if data["weight_lbs"] else None
    if "height_in" in data:
        patient.height_in = float(data["height_in"]) if data["height_in"] else None
    if "date_of_birth" in data and data["date_of_birth"]:
        patient.date_of_birth = date.fromisoformat(data["date_of_birth"])
    if "email" in data:
        patient.email = data["email"] or None

    db.session.commit()
    return jsonify(patient.to_dict()), 200


@patients_bp.route("/<int:patient_id>/summary", methods=["GET"])
@login_required
def summary(patient_id):
    """Full patient summary — latest check-in, active protocol, recent doses, labs."""
    patient = User.query.get_or_404(patient_id)
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403

    last_checkin = CheckIn.query.filter_by(patient_id=patient_id).order_by(CheckIn.date.desc()).first()
    active_protocol = Protocol.query.filter_by(patient_id=patient_id, active=True).first()

    # Adherence last 30 days
    from datetime import timedelta
    from sqlalchemy import text
    today = date.today()
    start = today - timedelta(days=30)
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM dose_logs WHERE patient_id = :pid AND date >= :start"
            ), {"pid": patient_id, "start": start})
            doses = result.scalar() or 0
    except Exception:
        doses = 0

    return jsonify({
        "patient":          patient.to_dict(),
        "last_checkin":     last_checkin.to_dict() if last_checkin else None,
        "active_protocol":  active_protocol.to_dict() if active_protocol else None,
        "doses_last_30d":   doses,
    }), 200
