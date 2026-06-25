from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import PushSubscription, User, Protocol, ProtocolItem, DoseLog
from datetime import date, datetime
import os
import json

push_bp = Blueprint("push", __name__)


@push_bp.route("/vapid-public-key", methods=["GET"])
def vapid_public_key():
    key = os.environ.get("VAPID_PUBLIC_KEY", "")
    return jsonify({"key": key}), 200


@push_bp.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    data     = request.get_json()
    endpoint = data.get("endpoint")
    p256dh   = data.get("keys", {}).get("p256dh")
    auth     = data.get("keys", {}).get("auth")

    if not endpoint or not p256dh or not auth:
        return jsonify({"error": "Invalid subscription data"}), 400

    # Update if exists, create if not
    existing = PushSubscription.query.filter_by(
        user_id=current_user.id, endpoint=endpoint
    ).first()

    if existing:
        existing.p256dh = p256dh
        existing.auth   = auth
    else:
        sub = PushSubscription(
            user_id=current_user.id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=request.headers.get("User-Agent", "")[:200],
        )
        db.session.add(sub)

    db.session.commit()
    return jsonify({"message": "Subscribed"}), 201


@push_bp.route("/unsubscribe", methods=["POST"])
@login_required
def unsubscribe():
    data     = request.get_json()
    endpoint = data.get("endpoint")
    if endpoint:
        PushSubscription.query.filter_by(
            user_id=current_user.id, endpoint=endpoint
        ).delete()
        db.session.commit()
    return jsonify({"message": "Unsubscribed"}), 200


def send_push(subscription, title, body, url="/"):
    """Send a push notification to a single subscription."""
    from pywebpush import webpush, WebPushException
    vapid_private = os.environ.get("VAPID_PRIVATE_KEY", "")
    vapid_email   = os.environ.get("VAPID_EMAIL", "mailto:admin@example.com")
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth":   subscription.auth,
                },
            },
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=vapid_private,
            vapid_claims={"sub": vapid_email},
        )
        return True
    except WebPushException as e:
        if e.response and e.response.status_code in (404, 410):
            # Subscription expired — delete it
            db.session.delete(subscription)
            db.session.commit()
        return False
    except Exception:
        return False


def send_dose_reminders():
    """Called by scheduled task — sends reminders for today's doses."""
    from models import ProtocolItem
    from datetime import datetime, time as dtime
    import pytz

    now_utc = datetime.utcnow()
    today   = date.today()

    # Get all active patients with push subscriptions
    patients_with_subs = db.session.query(User).join(
        PushSubscription, PushSubscription.user_id == User.id
    ).filter(User.role == "patient", User.active == True).all()

    sent = 0
    for patient in patients_with_subs:
        # Get active protocol items
        active_protocol = Protocol.query.filter_by(
            patient_id=patient.id, active=True
        ).first()
        if not active_protocol:
            continue

        items = ProtocolItem.query.filter_by(
            protocol_id=active_protocol.id, active=True
        ).all()
        if not items:
            continue

        # Check which items haven't been logged today
        logged_ids = {
            l.protocol_item_id for l in
            DoseLog.query.filter_by(patient_id=patient.id, date=today).all()
        }
        due_items = [i for i in items if i.id not in logged_ids]
        if not due_items:
            continue

        # Check reminder time for each item
        now_hour = now_utc.hour  # simplified — will improve with per-patient timezone later
        items_due_now = []
        for item in due_items:
            reminder_time = item.reminder_time  # e.g. "07:00"
            if reminder_time:
                try:
                    rh, rm = map(int, reminder_time.split(":"))
                    # Send if within 30 minutes of scheduled time
                    if abs(now_utc.hour * 60 + now_utc.minute - rh * 60 - rm) <= 30:
                        items_due_now.append(item)
                except Exception:
                    pass

        if not items_due_now:
            continue

        # Send notification
        names = ", ".join([i.compound.name for i in items_due_now if i.compound])
        subs  = PushSubscription.query.filter_by(user_id=patient.id).all()
        for sub in subs:
            if send_push(sub, "Dose reminder 💊", f"Time to take: {names}", "/"):
                sent += 1

    return sent
