c = open('/home/madfella/peptidetrack/routes/saved_calcs.py').read()

old_import = "from models import SavedCalc"
new_import = "from models import SavedCalc, SavedBlendCalc\nimport json"
n1 = c.count(old_import)
print("import count:", n1)
assert n1 == 1
c = c.replace(old_import, new_import, 1)

old_end = '''@saved_calcs_bp.route("/<int:calc_id>", methods=["DELETE"])
@login_required
def delete_calc(calc_id):
    calc = SavedCalc.query.get_or_404(calc_id)
    if calc.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(calc)
    db.session.commit()
    return jsonify({"deleted": True}), 200'''
new_end = old_end + '''


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


@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["DELETE"])
@login_required
def delete_blend_calc(blend_id):
    blend = SavedBlendCalc.query.get_or_404(blend_id)
    if blend.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(blend)
    db.session.commit()
    return jsonify({"deleted": True}), 200'''
n2 = c.count(old_end)
print("end count:", n2)
assert n2 == 1
c = c.replace(old_end, new_end, 1)

open('/home/madfella/peptidetrack/routes/saved_calcs.py', 'w').write(c)
print("written")
