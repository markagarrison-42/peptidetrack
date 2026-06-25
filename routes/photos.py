from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Photo
from datetime import date
import cloudinary
import cloudinary.uploader
import os

photos_bp = Blueprint("photos", __name__)


def init_cloudinary():
    cloudinary_url = os.environ.get("CLOUDINARY_URL")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url)


@photos_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_for_patient(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    query = Photo.query.filter_by(patient_id=patient_id)
    # Practitioners only see photos the patient has shared
    if current_user.role == "practitioner":
        query = query.filter_by(shared_with_practitioner=True)
    photos = query.order_by(Photo.date.desc()).all()
    return jsonify([p.to_dict() for p in photos]), 200


@photos_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    patient_id = current_user.id if current_user.role == "patient" else request.form.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id required"}), 400

    patient_id = int(patient_id)
    file       = request.files["file"]
    angle      = request.form.get("angle", "front")
    notes      = request.form.get("notes", "")
    photo_date = request.form.get("date") or date.today().isoformat()
    shared     = request.form.get("shared_with_practitioner", "true").lower() != "false"

    init_cloudinary()
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=f"peptidetrack/patient_{patient_id}",
            transformation=[{"width": 800, "crop": "limit"}],
        )
        photo = Photo(
            patient_id=patient_id,
            date=date.fromisoformat(photo_date),
            cloudinary_id=result["public_id"],
            cloudinary_url=result["secure_url"],
            angle=angle,
            notes=notes,
            shared_with_practitioner=shared,
        )
        db.session.add(photo)
        db.session.commit()
        return jsonify(photo.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@photos_bp.route("/<int:photo_id>/toggle-share", methods=["POST"])
@login_required
def toggle_share(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    photo.shared_with_practitioner = not photo.shared_with_practitioner
    db.session.commit()
    return jsonify(photo.to_dict()), 200


@photos_bp.route("/<int:photo_id>", methods=["DELETE"])
@login_required
def delete(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user.role == "patient" and photo.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    init_cloudinary()
    try:
        cloudinary.uploader.destroy(photo.cloudinary_id)
    except Exception:
        pass
    db.session.delete(photo)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
