from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import SavedCalc

saved_calcs_bp = Blueprint("saved_calcs", __name__)


@saved_calcs_bp.route("/", methods=["GET"])
@login_required
def list_calcs():
    calcs = SavedCalc.query.filter_by(patient_id=current_user.id).order_by(SavedCalc.created_at.desc()).all()
    return jsonify([c.to_dict() for c in calcs]), 200


@saved_calcs_bp.route("/", methods=["POST"])
@login_required
def create_calc():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    calc = SavedCalc(
        patient_id=current_user.id,
        name=name,
        vial_size=float(data["vial_size"]),
        unit=data.get("unit", "mg"),
        water=float(data["water"]),
        dose=float(data["dose"]),
    )
    db.session.add(calc)
    db.session.commit()
    return jsonify(calc.to_dict()), 201


@saved_calcs_bp.route("/<int:calc_id>", methods=["DELETE"])
@login_required
def delete_calc(calc_id):
    calc = SavedCalc.query.get_or_404(calc_id)
    if calc.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(calc)
    db.session.commit()
    return jsonify({"deleted": True}), 200
