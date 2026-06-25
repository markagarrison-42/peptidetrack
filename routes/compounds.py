from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Compound, TitrationTemplate

compounds_bp = Blueprint("compounds", __name__)


@compounds_bp.route("/", methods=["GET"])
@login_required
def get_all():
    compounds = Compound.query.filter_by(active=True).order_by(Compound.category, Compound.name).all()
    return jsonify([c.to_dict() for c in compounds]), 200


@compounds_bp.route("/", methods=["POST"])
@login_required
def create():
    data = request.get_json()
    name = data["name"].strip()
    # Reuse existing compound if name matches (case-insensitive)
    existing = Compound.query.filter(Compound.name.ilike(name)).first()
    if existing:
        return jsonify(existing.to_dict()), 200
    c = Compound(
        name=name,
        category=data.get("category", "Other"),
        default_route=data.get("default_route"),
        typical_dose_min=float(data["typical_dose_min"]) if data.get("typical_dose_min") else None,
        typical_dose_max=float(data["typical_dose_max"]) if data.get("typical_dose_max") else None,
        dose_unit=data.get("dose_unit", "mg"),
        frequency=data.get("frequency"),
        has_titration=bool(data.get("has_titration", False)),
        titration_notes=data.get("titration_notes"),
        notes=data.get("notes"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@compounds_bp.route("/<int:compound_id>", methods=["PUT"])
@login_required
def update(compound_id):
    if current_user.role != "practitioner":
        return jsonify({"error": "Unauthorized"}), 403
    c = Compound.query.get_or_404(compound_id)
    data = request.get_json()
    for field in ("name", "category", "default_route", "frequency", "dose_unit", "titration_notes", "notes"):
        if field in data:
            setattr(c, field, data[field])
    for field in ("typical_dose_min", "typical_dose_max"):
        if field in data:
            setattr(c, field, float(data[field]) if data[field] else None)
    if "has_titration" in data:
        c.has_titration = bool(data["has_titration"])
    if "active" in data:
        c.active = bool(data["active"])
    db.session.commit()
    return jsonify(c.to_dict()), 200


@compounds_bp.route("/<int:compound_id>/titration", methods=["GET"])
@login_required
def get_titration(compound_id):
    steps = TitrationTemplate.query.filter_by(compound_id=compound_id).order_by(TitrationTemplate.week_number).all()
    return jsonify([s.to_dict() for s in steps]), 200


@compounds_bp.route("/<int:compound_id>/titration", methods=["POST"])
@login_required
def add_titration_step(compound_id):
    if current_user.role != "practitioner":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    step = TitrationTemplate(
        compound_id=compound_id,
        week_number=int(data["week_number"]),
        dose_mg=float(data["dose_mg"]),
        notes=data.get("notes"),
    )
    db.session.add(step)
    db.session.commit()
    return jsonify(step.to_dict()), 201
