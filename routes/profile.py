from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, WeightLog, DiaryEntry
from datetime import date, datetime
profile_bp = Blueprint("profile", __name__)
# ── Profile ────────────────────────────────────────────
@profile_bp.route("/<int:patient_id>", methods=["GET"])
@login_required
def get_profile(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    patient = User.query.get_or_404(patient_id)
    return jsonify(patient.to_dict()), 200

@profile_bp.route("/<int:patient_id>", methods=["PUT"])
@login_required
def update_profile(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    patient = User.query.get_or_404(patient_id)
    data = request.get_json()
    for field in ("first_name", "last_name", "goals", "notes", "email", "sex"):
        if field in data:
            setattr(patient, field, data[field] or None)
    if "height_in" in data:
        patient.height_in = float(data["height_in"]) if data["height_in"] else None
    if "date_of_birth" in data and data["date_of_birth"]:
        patient.date_of_birth = date.fromisoformat(data["date_of_birth"])
    if "timezone_offset" in data and data["timezone_offset"] is not None:
        patient.timezone_offset = float(data["timezone_offset"])
    db.session.commit()
    return jsonify(patient.to_dict()), 200


# ── Weight log ─────────────────────────────────────────
@profile_bp.route("/<int:patient_id>/weight", methods=["GET"])
@login_required
def get_weight(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    logs = WeightLog.query.filter_by(patient_id=patient_id).order_by(WeightLog.date.desc()).limit(90).all()
    return jsonify([l.to_dict() for l in logs]), 200


@profile_bp.route("/<int:patient_id>/weight", methods=["POST"])
@login_required
def log_weight(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    log = WeightLog(
        patient_id=patient_id,
        date=date.fromisoformat(data["date"]),
        weight_lbs=float(data["weight_lbs"]),
        notes=data.get("notes"),
    )
    patient = User.query.get(patient_id)
    if patient:
        patient.weight_lbs = float(data["weight_lbs"])
    db.session.add(log)
    db.session.commit()
    return jsonify(log.to_dict()), 201


@profile_bp.route("/<int:patient_id>/weight/<int:log_id>", methods=["DELETE"])
@login_required
def delete_weight(patient_id, log_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    log = WeightLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


# ── Diary ──────────────────────────────────────────────
@profile_bp.route("/<int:patient_id>/diary", methods=["GET"])
@login_required
def get_diary(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    entries = DiaryEntry.query.filter_by(patient_id=patient_id).order_by(DiaryEntry.date.desc()).limit(50).all()
    return jsonify([e.to_dict() for e in entries]), 200


@profile_bp.route("/<int:patient_id>/diary", methods=["POST"])
@login_required
def create_diary(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if not data.get("body", "").strip():
        return jsonify({"error": "Entry body required"}), 400
    entry = DiaryEntry(
        patient_id=patient_id,
        date=date.fromisoformat(data["date"]),
        body=data["body"].strip(),
        mood_tag=data.get("mood_tag"),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@profile_bp.route("/<int:patient_id>/diary/<int:entry_id>", methods=["DELETE"])
@login_required
def delete_diary(patient_id, entry_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    entry = DiaryEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@profile_bp.route("/onboarding-complete", methods=["POST"])
@login_required
def onboarding_complete():
    current_user.onboarding_complete = True
    db.session.commit()
    return jsonify({"message": "Onboarding complete"}), 200
