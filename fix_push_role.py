content = open('/home/madfella/peptidetrack/routes/push.py').read()

old = "    ).filter(User.role == 'patient', User.active == True).all()"
new = "    ).filter(User.active == True).all()"

if old in content:
    content = content.replace(old, new)
    open('/home/madfella/peptidetrack/routes/push.py', 'w').write(content)
    print('done')
else:
    print('NOT FOUND')
    print(repr(content[content.find('patients_with_subs'):content.find('patients_with_subs')+200]))
