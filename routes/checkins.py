from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import CheckIn
from datetime import date

checkins_bp = Blueprint("checkins", __name__)


@checkins_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_for_patient(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    checkins = CheckIn.query.filter_by(patient_id=patient_id).order_by(CheckIn.date.desc()).all()
    return jsonify([c.to_dict() for c in checkins]), 200


@checkins_bp.route("/", methods=["POST"])
@login_required
def create():
    data = request.get_json()
    patient_id = current_user.id if current_user.role == "patient" else int(data.get("patient_id", current_user.id))

    side_effects = data.get("side_effects", [])
    if isinstance(side_effects, list):
        side_effects = ",".join(side_effects)

    checkin_date = date.fromisoformat(data["date"])
    c = CheckIn.query.filter_by(patient_id=patient_id, date=checkin_date).first()
    if c is None:
        c = CheckIn(patient_id=patient_id, date=checkin_date)
        db.session.add(c)

    def _num(field, conv):
        # Only overwrite when the field was actually provided (non-empty)
        if data.get(field) not in (None, ""):
            setattr(c, field, conv(data[field]))

    _num("weight_lbs", float)
    _num("energy", int)
    _num("mood", int)
    _num("sleep_quality", int)
    _num("libido", int)
    _num("appetite", int)
    _num("overall", int)
    _num("waist_in", float)
    _num("hips_in", float)
    _num("chest_in", float)
    _num("arms_in", float)
    _num("thighs_in", float)
    _num("neck_in", float)
    _num("calf_in", float)
    _num("body_fat_pct", float)
    if side_effects:
        c.side_effects = side_effects
    if data.get("notes") is not None:
        c.notes = data.get("notes")

    db.session.commit()
    return jsonify(c.to_dict()), 201


@checkins_bp.route("/<int:checkin_id>", methods=["DELETE"])
@login_required
def delete(checkin_id):
    c = CheckIn.query.get_or_404(checkin_id)
    if current_user.role == "patient" and c.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
