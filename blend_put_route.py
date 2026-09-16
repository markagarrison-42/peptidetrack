c = open('/home/madfella/peptidetrack/routes/saved_calcs.py').read()
old = '''@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["DELETE"])
@login_required
def delete_blend_calc(blend_id):'''
new = '''@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["PUT"])
@login_required
def update_blend_calc(blend_id):
    blend = SavedBlendCalc.query.get_or_404(blend_id)
    if blend.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    compounds = data.get("compounds", [])
    if not compounds:
        return jsonify({"error": "At least one compound is required"}), 400
    blend.name = name
    blend.water = float(data["water"])
    blend.vial_unit = data.get("vial_unit", "mg")
    blend.dose_unit = data.get("dose_unit", "mg")
    blend.compounds_json = json.dumps(compounds)
    db.session.commit()
    return jsonify(blend.to_dict()), 200


@saved_calcs_bp.route("/blends/<int:blend_id>", methods=["DELETE"])
@login_required
def delete_blend_calc(blend_id):'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/routes/saved_calcs.py', 'w').write(c)
print("written")
