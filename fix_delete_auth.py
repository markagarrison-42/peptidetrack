content = open('/home/madfella/peptidetrack/routes/protocols.py').read()

old = """def delete_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200"""

new = """def delete_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200"""

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/routes/protocols.py', 'w').write(content)
    print('delete_item ownership check: OK')
else:
    print('NOT FOUND')
