content = open('/home/madfella/peptidetrack/routes/protocols.py').read()

old = """def update_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    data = request.get_json()"""

new = """def update_item(item_id):
    item = ProtocolItem.query.get_or_404(item_id)
    # Security check: ensure item belongs to current user's protocol
    if current_user.role == 'patient' and item.protocol.patient_id != current_user.id:
        from flask import jsonify
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()"""

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/routes/protocols.py', 'w').write(content)
    print('Ownership check added: OK')
else:
    print('NOT FOUND')
    idx = content.find('def update_item')
    print(repr(content[idx:idx+200]))
