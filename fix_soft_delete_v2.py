import subprocess

# 1. Revert protocols.py to soft delete
content = open('/home/madfella/peptidetrack/routes/protocols.py').read()

# Find current delete_item implementation
idx = content.find('def delete_item')
end = content.find('\n@', idx)
print('Current delete_item:')
print(repr(content[idx:end][:400]))

old = """    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    # Soft delete — keeps dose history intact
    item.active = False
    db.session.commit()
    return jsonify({"message": "Removed"}), 200"""

# Check if already soft delete
if 'item.active = False' in content[idx:end]:
    print('Already soft delete')
else:
    # Find what's there and replace with soft delete
    import re
    # Find the block after the auth check
    auth_check = "    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:\n        return jsonify({\"error\": \"Unauthorized\"}), 403"
    after_auth = content.find(auth_check, idx)
    if after_auth > 0:
        # Find end of function
        fn_end = content.find('\n@', after_auth)
        old_fn = content[after_auth:fn_end]
        new_fn = auth_check + "\n    # Soft delete — hides from Today but keeps dose history\n    item.active = False\n    db.session.commit()\n    return jsonify({\"message\": \"Removed\"}), 200"
        content = content[:after_auth] + new_fn + content[fn_end:]
        print('Soft delete applied')

open('/home/madfella/peptidetrack/routes/protocols.py', 'w').write(content)

# 2. Update app.js - show ALL items (including inactive) in unscheduled picker
app = open('/home/madfella/peptidetrack/static/app.js').read()

# Find renderUnscheduledSection and update filter
old_filter = "proto.items.forEach(function(item) {\n      if (!item.active) return;"
new_filter = "proto.items.forEach(function(item) {\n      // Include inactive items so hidden compounds can still be logged"

if old_filter in app:
    app = app.replace(old_filter, new_filter)
    print('Unscheduled picker updated')
else:
    # Find it
    idx2 = app.find('renderUnscheduledSection')
    print('renderUnscheduledSection at:', idx2)
    print(repr(app[idx2:idx2+400]))

open('/home/madfella/peptidetrack/static/app.js', 'w').write(app)

result = subprocess.run(['node', '--check', '/home/madfella/peptidetrack/static/app.js'], capture_output=True, text=True)
print('JS:', 'VALID' if result.returncode == 0 else 'INVALID: ' + result.stderr[:200])
