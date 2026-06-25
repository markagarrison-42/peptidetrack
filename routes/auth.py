from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, mail
from models import User, InviteCode, PasswordResetToken
from flask_mail import Message
from datetime import datetime, timedelta
import secrets
import os

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data       = request.get_json()
    username   = (data.get("username") or "").strip().lower()
    password   = data.get("password") or ""
    email      = (data.get("email") or "").strip().lower() or None
    first_name = data.get("first_name") or None
    last_name  = data.get("last_name") or None

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    practitioner = User.query.filter_by(role="practitioner").first()

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="patient",
        practitioner_id=practitioner.id if practitioner else None,
        first_name=first_name,
        last_name=last_name,
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"message": "Account created", "username": user.username, "role": user.role}), 201


@auth_bp.route("/register-practitioner", methods=["POST"])
def register_practitioner():
    """First-run only — creates the practitioner account."""
    if User.query.filter_by(role="practitioner").count() > 0:
        return jsonify({"error": "Practitioner account already exists"}), 403

    data     = request.get_json()
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    email    = (data.get("email") or "").strip().lower() or None
    secret   = data.get("setup_secret") or ""

    if secret != os.environ.get("SETUP_SECRET", "setup-mg42"):
        return jsonify({"error": "Invalid setup secret"}), 403
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="practitioner",
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({"message": "Practitioner account created", "username": user.username, "role": user.role}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Logged in", "username": user.username, "role": user.role}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id":       current_user.id,
        "username": current_user.username,
        "role":     current_user.role,
        "full_name": current_user.full_name,
    }), 200


@auth_bp.route("/invite", methods=["POST"])
@login_required
def create_invite():
    if current_user.role != "practitioner":
        return jsonify({"error": "Unauthorized"}), 403

    code = secrets.token_hex(4).upper()  # e.g. A3F2C1B9
    while InviteCode.query.filter_by(code=code).first():
        code = secrets.token_hex(4).upper()

    invite = InviteCode(
        code=code,
        practitioner_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.session.add(invite)
    db.session.commit()
    return jsonify(invite.to_dict()), 201


@auth_bp.route("/invites", methods=["GET"])
@login_required
def list_invites():
    if current_user.role != "practitioner":
        return jsonify({"error": "Unauthorized"}), 403
    invites = InviteCode.query.filter_by(practitioner_id=current_user.id).order_by(InviteCode.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invites]), 200


@auth_bp.route("/reset/request", methods=["POST"])
def request_reset():
    data     = request.get_json()
    username = (data.get("username") or "").strip().lower()
    if not username:
        return jsonify({"error": "Username required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "If that username exists, a reset email has been sent"}), 200

    email = user.email if user.email else (username if "@" in username else None)
    if not email:
        return jsonify({"error": "No email on file for this account"}), 400

    PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({"used": True})
    token  = secrets.token_urlsafe(32)
    reset  = PasswordResetToken(user_id=user.id, token=token, expires_at=datetime.utcnow() + timedelta(hours=1))
    db.session.add(reset)
    db.session.commit()

    base_url   = os.environ.get("APP_URL", "https://protocol.mg42health.com")
    reset_link = f"{base_url}/reset-password?token={token}"

    try:
        msg = Message(
            subject="PeptideTrack — Password Reset",
            recipients=[email],
            body=f"Hi {username},\n\nReset your PeptideTrack password:\n\n{reset_link}\n\nExpires in 1 hour.\n\n— PeptideTrack"
        )
        mail.send(msg)
    except Exception as e:
        return jsonify({"error": "Failed to send email: " + str(e)}), 500

    return jsonify({"message": "Reset email sent"}), 200


@auth_bp.route("/reset/confirm", methods=["POST"])
def confirm_reset():
    data     = request.get_json()
    token    = data.get("token") or ""
    password = data.get("password") or ""

    if not token or not password or len(password) < 6:
        return jsonify({"error": "Token and password (min 6 chars) required"}), 400

    reset = PasswordResetToken.query.filter_by(token=token).first()
    if not reset or not reset.is_valid():
        return jsonify({"error": "Invalid or expired reset link"}), 400

    user = User.query.get(reset.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 400

    user.password_hash = generate_password_hash(password)
    reset.used = True
    db.session.commit()
    return jsonify({"message": "Password reset successfully"}), 200


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json()
    current_pw  = data.get("current_password") or ""
    new_pw      = data.get("new_password") or ""

    if not check_password_hash(current_user.password_hash, current_pw):
        return jsonify({"error": "Current password is incorrect"}), 400
    if len(new_pw) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    current_user.password_hash = generate_password_hash(new_pw)
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200


@auth_bp.route("/change-username", methods=["POST"])
@login_required
def change_username():
    data     = request.get_json()
    username = (data.get("username") or "").strip().lower()

    if not username:
        return jsonify({"error": "Username required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    current_user.username = username
    db.session.commit()
    return jsonify({"message": "Username updated", "username": username}), 200
