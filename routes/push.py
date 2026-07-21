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
            db.session.delete(subscription)
            db.session.commit()
        return False
    except Exception:
        return False


# Day abbreviation map matching what we store in frequency field
DAY_ABBREVS = {
    0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'
}

NON_SPECIFIC = {'Daily', 'Weekly', 'Twice daily', '3x/week', 'Monthly', 'As needed'}


def is_scheduled_today(item, today_weekday):
    """Check if a protocol item is scheduled for today."""
    freq = item.frequency or 'Daily'
    if freq in NON_SPECIFIC:
        # Daily and others always count (simplified)
        return True
    # Specific days — check if today's abbreviation is in the list
    today_abbrev = DAY_ABBREVS[today_weekday]
    days = [d.strip() for d in freq.split(',')]
    return today_abbrev in days


def send_dose_reminders():
    """Called by scheduled task — sends reminders for due doses."""
    now_utc       = datetime.utcnow()
    now_utc_mins  = now_utc.hour * 60 + now_utc.minute

    # Get all active patients with push subscriptions
    patients_with_subs = db.session.query(User).join(
        PushSubscription, PushSubscription.user_id == User.id
    ).filter(User.active == True).all()

    sent = 0
    for patient in patients_with_subs:
        # Get all active protocols
        protocols = Protocol.query.filter_by(
            patient_id=patient.id, active=True
        ).all()
        if not protocols:
            continue

        # Calculate patient's local time using their timezone offset
        tz_offset     = patient.timezone_offset if patient.timezone_offset is not None else -5.0
        local_mins    = (now_utc_mins + int(tz_offset * 60)) % (24 * 60)
        local_dt      = now_utc + __import__('datetime').timedelta(hours=tz_offset)
        today         = local_dt.date()
        today_weekday = today.weekday()

        # Get all logged/skipped item ids for today (local date)
        logged_ids = {
            l.protocol_item_id for l in
            DoseLog.query.filter_by(patient_id=patient.id, date=today).all()
        }

        items_due_now = []
        for protocol in protocols:
            items = ProtocolItem.query.filter_by(
                protocol_id=protocol.id, active=True
            ).all()
            for item in items:
                # Skip if no reminder time set
                if not item.reminder_time:
                    continue
                # Skip if already logged or skipped today
                if item.id in logged_ids:
                    continue
                # Skip if not scheduled for today
                if not is_scheduled_today(item, today_weekday):
                    continue
                # Check if reminder time matches now (within 5 minutes)
                try:
                    rh, rm = map(int, item.reminder_time.split(':'))
                    reminder_mins = rh * 60 + rm
                    if abs(local_mins - reminder_mins) <= 5:
                        items_due_now.append(item)
                except Exception:
                    continue

        if not items_due_now:
            continue

        names = ', '.join([i.compound.name for i in items_due_now if i.compound])
        subs  = PushSubscription.query.filter_by(user_id=patient.id).all()
        for sub in subs:
            if send_push(sub, '💊 Dose reminder', f'Time to take: {names}', '/'):
                sent += 1

    return sent
