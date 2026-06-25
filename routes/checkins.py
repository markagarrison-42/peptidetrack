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

    c = CheckIn(
        patient_id=patient_id,
        date=date.fromisoformat(data["date"]),
        weight_lbs=float(data["weight_lbs"]) if data.get("weight_lbs") else None,
        energy=int(data["energy"]) if data.get("energy") else None,
        mood=int(data["mood"]) if data.get("mood") else None,
        sleep_quality=int(data["sleep_quality"]) if data.get("sleep_quality") else None,
        libido=int(data["libido"]) if data.get("libido") else None,
        appetite=int(data["appetite"]) if data.get("appetite") else None,
        overall=int(data["overall"]) if data.get("overall") else None,
        side_effects=side_effects or None,
        notes=data.get("notes"),
        waist_in=float(data["waist_in"]) if data.get("waist_in") else None,
        hips_in=float(data["hips_in"]) if data.get("hips_in") else None,
        chest_in=float(data["chest_in"]) if data.get("chest_in") else None,
        arms_in=float(data["arms_in"]) if data.get("arms_in") else None,
        thighs_in=float(data["thighs_in"]) if data.get("thighs_in") else None,
        neck_in=float(data["neck_in"]) if data.get("neck_in") else None,
    )
    db.session.add(c)
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
