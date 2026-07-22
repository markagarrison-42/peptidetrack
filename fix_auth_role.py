content = open('/home/madfella/peptidetrack/routes/protocols.py').read()

# Fix update_item - practitioners can edit any item, patients only their own
old_update = """    # Security check: ensure item belongs to current user's protocol
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403"""

new_update = """    # Security check: patients can only edit their own items
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403"""

# Fix delete_item same way
old_delete = """    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(item)"""

new_delete = """    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(item)"""

if old_update in content:
    content = content.replace(old_update, new_update)
    print('update_item fixed: OK')
else:
    print('update_item NOT FOUND')

if old_delete in content:
    content = content.replace(old_delete, new_delete)
    print('delete_item fixed: OK')
else:
    print('delete_item NOT FOUND')

open('/home/madfella/peptidetrack/routes/protocols.py', 'w').write(content)
print('saved')
