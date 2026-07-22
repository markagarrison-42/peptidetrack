content = open('/home/madfella/peptidetrack/routes/doses.py').read()

# Fix today() route
old_today = """def today():
    patient_id = current_user.id
    today_date = date.today()
    logs = DoseLog.query.filter_by(patient_id=patient_id, date=today_date).all()
    taken_ids   = [l.protocol_item_id for l in logs if not l.skipped]
    skipped_ids = [l.protocol_item_id for l in logs if l.skipped]
    return jsonify({"date": today_date.isoformat(), "taken_item_ids": taken_ids, "skipped_item_ids": skipped_ids}), 200"""

new_today = """def today():
    patient_id = current_user.id
    local_date_str = request.args.get('local_date')
    try:
        today_date = date.fromisoformat(local_date_str) if local_date_str else date.today()
    except ValueError:
        today_date = date.today()
    logs = DoseLog.query.filter_by(patient_id=patient_id, date=today_date).all()
    taken_ids   = [l.protocol_item_id for l in logs if not l.skipped]
    skipped_ids = [l.protocol_item_id for l in logs if l.skipped]
    return jsonify({"date": today_date.isoformat(), "taken_item_ids": taken_ids, "skipped_item_ids": skipped_ids}), 200"""

if old_today in content:
    content = content.replace(old_today, new_today)
    print('today() fixed')
else:
    print('today() NOT FOUND')

# Fix toggle() route - find and add local_date support
old_toggle = """    item_id    = int(data["protocol_item_id"])
    today_date = date.today()
    patient_id = current_user.id"""

new_toggle = """    item_id    = int(data["protocol_item_id"])
    local_date_str = data.get("local_date")
    try:
        today_date = date.fromisoformat(local_date_str) if local_date_str else date.today()
    except ValueError:
        today_date = date.today()
    patient_id = current_user.id"""

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle)
    print('toggle() fixed')
else:
    print('toggle() NOT FOUND')

# Fix skip() route
old_skip = """    item_id = int(data["protocol_item_id"])
    today_date = date.today()
    patient_id = current_user.id"""

new_skip = """    item_id = int(data["protocol_item_id"])
    local_date_str = data.get("local_date")
    try:
        today_date = date.fromisoformat(local_date_str) if local_date_str else date.today()
    except ValueError:
        today_date = date.today()
    patient_id = current_user.id"""

if old_skip in content:
    content = content.replace(old_skip, new_skip)
    print('skip() fixed')
else:
    print('skip() NOT FOUND')

open('/home/madfella/peptidetrack/routes/doses.py', 'w').write(content)
print('Done - local_date count:', content.count('local_date'))
