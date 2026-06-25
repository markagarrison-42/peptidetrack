from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Lab, LabAttachment
from datetime import date
import cloudinary
import cloudinary.uploader
import os

labs_bp = Blueprint("labs", __name__)

COMMON_LABS = [
    "IGF-1", "Testosterone Total", "Testosterone Free", "Estradiol",
    "LH", "FSH", "TSH", "Free T4", "Free T3",
    "HbA1c", "Fasting Glucose", "Fasting Insulin",
    "Total Cholesterol", "LDL", "HDL", "Triglycerides",
    "CRP", "Homocysteine", "Vitamin D", "Cortisol",
    "DHEA-S", "Prolactin", "PSA", "CBC", "CMP",
]


@labs_bp.route("/patient/<int:patient_id>", methods=["GET"])
@login_required
def get_for_patient(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    labs = Lab.query.filter_by(patient_id=patient_id).order_by(Lab.date.desc()).all()
    return jsonify([l.to_dict() for l in labs]), 200


@labs_bp.route("/", methods=["POST"])
@login_required
def create():
    if current_user.role != "practitioner":
        return jsonify({"error": "Practitioner access required"}), 403
    data = request.get_json()
    lab = Lab(
        patient_id=int(data["patient_id"]),
        date=date.fromisoformat(data["date"]),
        test_name=data["test_name"].strip(),
        value=float(data["value"]),
        unit=data.get("unit"),
        ref_range_low=float(data["ref_range_low"]) if data.get("ref_range_low") else None,
        ref_range_high=float(data["ref_range_high"]) if data.get("ref_range_high") else None,
        notes=data.get("notes"),
        entered_by_id=current_user.id,
    )
    db.session.add(lab)
    db.session.commit()
    return jsonify(lab.to_dict()), 201


@labs_bp.route("/<int:lab_id>", methods=["DELETE"])
@login_required
def delete(lab_id):
    if current_user.role != "practitioner":
        return jsonify({"error": "Unauthorized"}), 403
    lab = Lab.query.get_or_404(lab_id)
    db.session.delete(lab)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@labs_bp.route("/common-tests", methods=["GET"])
@login_required
def common_tests():
    return jsonify(COMMON_LABS), 200


def init_cloudinary():
    url = os.environ.get("CLOUDINARY_URL")
    if url:
        cloudinary.config(cloudinary_url=url)


@labs_bp.route("/attachment/upload", methods=["POST"])
@login_required
def upload_attachment():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    patient_id = current_user.id if current_user.role == "patient" else request.form.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id required"}), 400

    patient_id = int(patient_id)
    file = request.files["file"]
    lab_date = request.form.get("date") or date.today().isoformat()
    notes = request.form.get("notes", "")

    init_cloudinary()
    try:
        # Detect file type
        filename = file.filename or ""
        is_pdf = filename.lower().endswith(".pdf") or file.content_type == "application/pdf"

        result = cloudinary.uploader.upload(
            file,
            folder=f"peptidetrack/labs/patient_{patient_id}",
            resource_type="auto",
        )

        attachment = LabAttachment(
            patient_id=patient_id,
            date=date.fromisoformat(lab_date),
            cloudinary_id=result["public_id"],
            cloudinary_url=result["secure_url"],
            file_type="pdf" if is_pdf else "image",
            notes=notes,
        )
        db.session.add(attachment)
        db.session.commit()
        return jsonify(attachment.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@labs_bp.route("/attachments/<int:patient_id>", methods=["GET"])
@login_required
def get_attachments(patient_id):
    if current_user.role == "patient" and current_user.id != patient_id:
        return jsonify({"error": "Unauthorized"}), 403
    attachments = LabAttachment.query.filter_by(patient_id=patient_id).order_by(LabAttachment.date.desc()).all()
    return jsonify([a.to_dict() for a in attachments]), 200


@labs_bp.route("/attachment/<int:att_id>", methods=["DELETE"])
@login_required
def delete_attachment(att_id):
    att = LabAttachment.query.get_or_404(att_id)
    if current_user.role == "patient" and att.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    init_cloudinary()
    try:
        cloudinary.uploader.destroy(att.cloudinary_id)
    except Exception:
        pass
    db.session.delete(att)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
