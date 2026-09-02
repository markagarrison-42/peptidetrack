c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''      html += '<button onclick="removeCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-size:12px;cursor:pointer">✕</button>';'''
new = '''      html += '<button onclick="removeCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:11px 14px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-size:12px;cursor:pointer">✕</button>';'''
n = c.count(old)
print("count:", n)
if n == 1:
    c = c.replace(old, new, 1)
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
    print("written")
else:
    print("ABORTED")
