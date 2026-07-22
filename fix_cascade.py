content = open('/home/madfella/peptidetrack/models.py').read()

old = '    protocol_item = db.relationship("ProtocolItem", backref="dose_logs", lazy=True)'
new = '    protocol_item = db.relationship("ProtocolItem", backref="dose_logs", lazy=True, passive_deletes=True)'

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/models.py', 'w').write(content)
    print('Fixed: OK')
else:
    print('NOT FOUND')
    idx = content.find('dose_logs')
    print(repr(content[idx-50:idx+100]))
