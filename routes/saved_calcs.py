from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import SavedCalc, SavedBlendCalc
import json

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
        dose_unit=data.get("dose_unit", data.get("unit", "mg")),
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


@saved_calcs_bp.route("/blends", methods=["GET"])
@login_required
def list_blend_calcs():
    blends = SavedBlendCalc.query.filter_by(patient_id=current_user.id).order_by(SavedBlendCalc.created_at.desc()).all()
    return jsonify([b.to_dict() for b in blends]), 200


@saved_calcs_bp.route("/blends", methods=["POST"])
@login_required
def create_blend_calc():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    compounds = data.get("compounds", [])
    if not compounds:
        return jsonify({"error": "At least one compound is required"}), 400
    blend = SavedBlendCalc(
        patient_id=current_user.id,
        name=name,
        water=float(data["water"]),
        vial_unit=data.get("vial_unit", "mg"),
        dose_unit=data.get("dose_unit", "mg"),
        compounds_json=json.dumps(compounds),
    )
    db.session.add(blend)
    db.session.commit()
    return jsonify(blend.to_dict()), 201


@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["PUT"])
@login_required
def update_blend_calc(blend_id):
    blend = SavedBlendCalc.query.get_or_404(blend_id)
    if blend.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    compounds = data.get("compounds", [])
    if not compounds:
        return jsonify({"error": "At least one compound is required"}), 400
    blend.name = name
    blend.water = float(data["water"])
    blend.vial_unit = data.get("vial_unit", "mg")
    blend.dose_unit = data.get("dose_unit", "mg")
    blend.compounds_json = json.dumps(compounds)
    db.session.commit()
    return jsonify(blend.to_dict()), 200


@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["DELETE"])
@login_required
def delete_blend_calc(blend_id):
    blend = SavedBlendCalc.query.get_or_404(blend_id)
    if blend.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(blend)
    db.session.commit()
    return jsonify({"deleted": True}), 200
