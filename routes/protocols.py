from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Protocol, ProtocolItem, Compound, User, TitrationTemplate, ProtocolItemHistory
from datetime import date

protocols_bp = Blueprint("protocols", __name__)


@protocols_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_for_patient(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    protocols = Protocol.query.filter_by(patient_id=patient_id).order_by(Protocol.created_at.desc()).all()
    return jsonify([p.to_dict() for p in protocols]), 200


@protocols_bp.route("/", methods=["POST"])
@login_required
def create():
    data = request.get_json()
    patient_id = int(data["patient_id"]) if data.get("patient_id") else current_user.id
    p = Protocol(
        patient_id=patient_id,
        practitioner_id=current_user.id,
        name=data["name"].strip(),
        phase=data.get("phase", "Loading"),
        start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
        review_date=date.fromisoformat(data["review_date"]) if data.get("review_date") else None,
        notes=data.get("notes"),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@protocols_bp.route("/<int:protocol_id>", methods=["PUT"])
@login_required
def update(protocol_id):
    p = Protocol.query.get_or_404(protocol_id)
    data = request.get_json()
    for field in ("name", "phase", "notes"):
        if field in data:
            setattr(p, field, data[field])
    if "active" in data:
        p.active = bool(data["active"])
    if "start_date" in data and data["start_date"]:
        p.start_date = date.fromisoformat(data["start_date"])
    if "review_date" in data and data["review_date"]:
        p.review_date = date.fromisoformat(data["review_date"])
    db.session.commit()
    return jsonify(p.to_dict()), 200


@protocols_bp.route("/<int:protocol_id>/items", methods=["POST"])
@login_required
def add_item(protocol_id):
    data = request.get_json()
    item = ProtocolItem(
        protocol_id=protocol_id,
        compound_id=int(data["compound_id"]),
        dose_mg=float(data["dose_mg"]),
        frequency=data["frequency"],
        route=data.get("route"),
        timing=data.get("timing"),
        phase=data.get("phase"),
        vial_size_mg=float(data["vial_size_mg"]) if data.get("vial_size_mg") else None,
        recon_volume_ml=float(data["recon_volume_ml"]) if data.get("recon_volume_ml") else None,
        notes=data.get("notes"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@protocols_bp.route("/items/<int:item_id>", methods=["PUT"])
@login_required
def update_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    # Security check: ensure item belongs to current user's protocol
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    for field in ("frequency", "route", "timing", "phase", "notes", "reminder_time"):
        if field in data:
            old_val = getattr(item, field)
            new_val = data[field]
            if str(old_val) != str(new_val) and field in ("phase", "frequency"):
                db.session.add(ProtocolItemHistory(
                    protocol_item_id=item.id,
                    changed_by_id=current_user.id,
                    field_changed=field,
                    old_value=str(old_val) if old_val else None,
                    new_value=str(new_val) if new_val else None,
                ))
            setattr(item, field, data[field])
    for field in ("dose_mg", "vial_size_mg", "recon_volume_ml"):
        if field in data:
            old_val = getattr(item, field)
            new_val = float(data[field]) if data[field] else None
            if field == "dose_mg" and old_val != new_val:
                db.session.add(ProtocolItemHistory(
                    protocol_item_id=item.id,
                    changed_by_id=current_user.id,
                    field_changed="dose_mg",
                    old_value=str(old_val) if old_val else None,
                    new_value=str(new_val) if new_val else None,
                ))
            setattr(item, field, new_val)
    if "dose_mg" in data:
        item.dose_overridden = True
    if "dose_overridden" in data:
        item.dose_overridden = bool(data["dose_overridden"])
    if "active" in data:
        item.active = bool(data["active"])
    db.session.commit()
    return jsonify(item.to_dict()), 200


@protocols_bp.route("/items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@protocols_bp.route("/<int:protocol_id>/suggest-dose", methods=["GET"])
@login_required
def suggest_dose(protocol_id):
    """Suggest next dose based on titration schedule and protocol start date."""
    p = Protocol.query.get_or_404(protocol_id)
    if not p.start_date:
        return jsonify({"suggestion": None}), 200

    from datetime import date, timedelta
    weeks_on = (date.today() - p.start_date).days // 7

    suggestions = []
    for item in p.items:
        if not item.active:
            continue
        steps = TitrationTemplate.query.filter_by(compound_id=item.compound_id).order_by(TitrationTemplate.week_number).all()
        if not steps:
            continue
        current_step = next((s for s in reversed(steps) if s.week_number <= weeks_on), steps[0])
        next_step    = next((s for s in steps if s.week_number > weeks_on), None)
        suggestions.append({
            "compound":          item.compound.name,
            "compound_id":       item.compound_id,
            "current_dose":      item.dose_mg,
            "suggested_dose":    current_step.dose_mg,
            "dose_overridden":   item.dose_overridden,
            "next_increase":     {"week": next_step.week_number, "dose_mg": next_step.dose_mg} if next_step else None,
            "weeks_on_protocol": weeks_on,
        })

    return jsonify({"suggestions": suggestions}), 200


@protocols_bp.route("/<int:protocol_id>/history", methods=["GET"])
@login_required
def get_history(protocol_id):
    p = Protocol.query.get_or_404(protocol_id)
    if current_user.role == "patient" and p.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    history = []
    for item in p.items:
        for h in sorted(item.history, key=lambda x: x.changed_at, reverse=True):
            d = h.to_dict()
            d["compound_name"] = item.compound.name if item.compound else None
            history.append(d)
    history.sort(key=lambda x: x["changed_at"], reverse=True)
    return jsonify(history), 200
