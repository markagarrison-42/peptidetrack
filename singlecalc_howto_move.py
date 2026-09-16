c = open('/home/madfella/peptidetrack/static/app.js').read()

old_remove = '''    '</div></div></div>' +
    '<div class="card" style="margin-top:4px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter your vial size (printed on the vial)<br>' +
    '2. Enter how much bac water you added<br>' +
    '3. Enter your prescribed dose<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>' +
    '<div class="section-label" style="margin-top:20px">Saved calculations</div>' +'''
new_remove = '''    '</div></div></div>' +
    '<div class="section-label" style="margin-top:20px">Saved calculations</div>' +'''
n1 = c.count(old_remove)
print("remove count:", n1)
assert n1 == 1
c = c.replace(old_remove, new_remove, 1)

old_insert = '''    '<div class="section-label">Reconstitution calculator</div>' +
    '<div class="card"><div class="card-body">' +'''
new_insert = '''    '<div class="section-label">Reconstitution calculator</div>' +
    '<div class="card" style="margin-bottom:12px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter your vial size (printed on the vial)<br>' +
    '2. Enter how much bac water you added<br>' +
    '3. Enter your prescribed dose<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>' +
    '<div class="card"><div class="card-body">' +'''
n2 = c.count(old_insert)
print("insert count:", n2)
assert n2 == 1
c = c.replace(old_insert, new_insert, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
