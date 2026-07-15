from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import DoseLog, ProtocolItem, Protocol
from datetime import date, timedelta

doses_bp = Blueprint("doses", __name__)


@doses_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_for_patient(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    logs = DoseLog.query.filter_by(patient_id=patient_id).order_by(DoseLog.date.desc(), DoseLog.created_at.desc()).limit(100).all()
    return jsonify([l.to_dict() for l in logs]), 200


@doses_bp.route("/today", methods=["GET"])
@login_required
def today():
    patient_id = current_user.id
    today_date = date.today()
    logs = DoseLog.query.filter_by(patient_id=patient_id, date=today_date).all()
    taken_ids   = [l.protocol_item_id for l in logs if not l.skipped]
    skipped_ids = [l.protocol_item_id for l in logs if l.skipped]
    return jsonify({"date": today_date.isoformat(), "taken_item_ids": taken_ids, "skipped_item_ids": skipped_ids}), 200


@doses_bp.route("/toggle", methods=["POST"])
@login_required
def toggle():
    data = request.get_json()
    item_id    = int(data["protocol_item_id"])
    today_date = date.today()
    patient_id = current_user.id

    item = ProtocolItem.query.get_or_404(item_id)

    existing = DoseLog.query.filter_by(
        patient_id=patient_id,
        protocol_item_id=item_id,
        date=today_date,
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"taken": False, "protocol_item_id": item_id}), 200
    else:
        log = DoseLog(
            patient_id=patient_id,
            protocol_item_id=item_id,
            date=today_date,
            dose_mg_taken=float(data.get("dose_mg_taken") or item.dose_mg),
            injection_site=data.get("injection_site"),
            notes=data.get("notes"),
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"taken": True, "protocol_item_id": item_id}), 201


@doses_bp.route("/skip", methods=["POST"])
@login_required
def skip():
    data = request.get_json()
    item_id    = int(data["protocol_item_id"])
    today_date = date.today()
    patient_id = current_user.id
    item = ProtocolItem.query.get_or_404(item_id)
    # Remove any existing log for today (taken or skipped)
    existing = DoseLog.query.filter_by(
        patient_id=patient_id,
        protocol_item_id=item_id,
        date=today_date,
    ).first()
    if existing:
        db.session.delete(existing)
    log = DoseLog(
        patient_id=patient_id,
        protocol_item_id=item_id,
        date=today_date,
        dose_mg_taken=None,
        skipped=True,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"skipped": True, "protocol_item_id": item_id}), 201


@doses_bp.route("/log-unscheduled", methods=["POST"])
@login_required
def log_unscheduled():
    data = request.get_json()
    item_id = int(data["protocol_item_id"])
    today_date = date.today()
    patient_id = current_user.id
    item = ProtocolItem.query.get_or_404(item_id)
    log = DoseLog(
        patient_id=patient_id,
        protocol_item_id=item_id,
        date=today_date,
        dose_mg_taken=float(data.get("dose_mg_taken") or item.dose_mg),
        notes=data.get("notes"),
        off_schedule=True,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"logged": True, "compound": item.compound.name}), 201


@doses_bp.route("/history", methods=["GET"])
@login_required
def history():
    offset = int(request.args.get("days_offset", 0))
    rng    = int(request.args.get("range", 30))
    today_date = date.today()
    end    = today_date - timedelta(days=offset)
    start  = end - timedelta(days=rng - 1)
    logs   = DoseLog.query.filter(
        DoseLog.patient_id == current_user.id,
        DoseLog.date >= start,
        DoseLog.date <= end,
    ).order_by(DoseLog.date.desc(), DoseLog.created_at.desc()).all()
    return jsonify([l.to_dict() for l in logs]), 200


@doses_bp.route("/logs/<int:log_id>", methods=["PUT"])
@login_required
def update_log(log_id):
    log = DoseLog.query.get_or_404(log_id)
    if log.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if "dose_mg_taken" in data:
        log.dose_mg_taken = float(data["dose_mg_taken"])
    if "notes" in data:
        log.notes = data["notes"] or None
    db.session.commit()
    return jsonify(log.to_dict()), 200


@doses_bp.route("/logs/<int:log_id>", methods=["DELETE"])
@login_required
def delete_log(log_id):
    log = DoseLog.query.get_or_404(log_id)
    if log.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(log)
    db.session.commit()
    return jsonify({"deleted": True}), 200


@doses_bp.route("/adherence/<int:patient_id>", methods=["GET"])
@login_required
def adherence(patient_id):
    """Return daily adherence % for last 30 days."""
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403

    days  = int(request.args.get("days", 30))
    today = date.today()
    start = today - timedelta(days=days - 1)

    active_protocol = Protocol.query.filter_by(patient_id=patient_id, active=True).first()
    if not active_protocol:
        return jsonify({}), 200

    total_items = ProtocolItem.query.filter_by(protocol_id=active_protocol.id, active=True).count()
    if total_items == 0:
        return jsonify({}), 200

    logs = DoseLog.query.filter(
        DoseLog.patient_id == patient_id,
        DoseLog.date >= start,
        DoseLog.date <= today,
    ).all()

    by_date = {}
    for l in logs:
        k = l.date.isoformat()
        by_date[k] = by_date.get(k, 0) + 1

    result = {}
    current = start
    while current <= today:
        k = current.isoformat()
        result[k] = round(by_date.get(k, 0) / total_items * 100)
        current += timedelta(days=1)

    return jsonify(result), 200
