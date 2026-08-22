from flask import Blueprint, request, jsonify
from extensions import db
from models import ApiToken, CheckIn
from datetime import date, datetime, timedelta

health_sync_bp = Blueprint("health_sync", __name__)

RECENT_DAYS_WINDOW = 3

METRIC_FIELD_MAP = {
    "weight_body_mass":     ("weight_lbs",   float),
    "body_fat_percentage":  ("body_fat_pct", float),
    "waist_circumference":  ("waist_in",     float),
}


def _authenticate():
    token_value = request.headers.get("X-API-Key")
    if not token_value:
        return None
    token = ApiToken.query.filter_by(token=token_value).first()
    return token.patient_id if token else None


@health_sync_bp.route("/sync", methods=["POST"])
def sync():
    patient_id = _authenticate()
    if not patient_id:
        return jsonify({"error": "Invalid or missing API key"}), 401

    payload = request.get_json(silent=True) or {}
    metrics = payload.get("data", {}).get("metrics", [])

    today = date.today()
    cutoff = today - timedelta(days=RECENT_DAYS_WINDOW)

    written = {}
    skipped_old = 0
    unmapped = set()

    for metric in metrics:
        name = metric.get("name")
        mapping = METRIC_FIELD_MAP.get(name)
        if not mapping:
            unmapped.add(name)
            continue
        field, conv = mapping

        for point in metric.get("data", []):
            raw_date = point.get("date", "")
            entry_date_str = raw_date.split(" ")[0]
            try:
                entry_date = date.fromisoformat(entry_date_str)
            except ValueError:
                continue
            if entry_date < cutoff or entry_date > today:
                skipped_old += 1
                continue

            qty = point.get("qty")
            if qty is None:
                continue

            c = CheckIn.query.filter_by(patient_id=patient_id, date=entry_date).first()
            if c is None:
                c = CheckIn(patient_id=patient_id, date=entry_date)
                db.session.add(c)
            setattr(c, field, conv(qty))
            written[entry_date.isoformat() + ":" + field] = conv(qty)

    db.session.commit()

    return jsonify({
        "synced_fields": len(written),
        "skipped_out_of_window": skipped_old,
        "unmapped_metrics": list(unmapped),
    }), 200
