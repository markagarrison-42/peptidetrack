c = open('/home/madfella/peptidetrack/routes/saved_calcs.py').read()
old = '''    calc = SavedCalc(
        patient_id=current_user.id,
        name=name,
        vial_size=float(data["vial_size"]),
        unit=data.get("unit", "mg"),
        water=float(data["water"]),
        dose=float(data["dose"]),
    )'''
new = '''    calc = SavedCalc(
        patient_id=current_user.id,
        name=name,
        vial_size=float(data["vial_size"]),
        unit=data.get("unit", "mg"),
        water=float(data["water"]),
        dose=float(data["dose"]),
        dose_unit=data.get("dose_unit", data.get("unit", "mg")),
    )'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/routes/saved_calcs.py', 'w').write(c)
print("written")
