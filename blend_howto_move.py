c = open('/home/madfella/peptidetrack/static/app.js').read()

old_remove = '''  html += '</div></div>';
  html += '</div>';
  html += '<div class="card" style="margin-top:4px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter how much bac water you added<br>' +
    '2. Enter each compound\\'s name and amount in the vial<br>' +
    '3. Enter your desired dose for ONE compound \\u2014 the others calculate automatically<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';'''
new_remove = '''  html += '</div></div>';
  html += '</div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';'''
n1 = c.count(old_remove)
print("remove count:", n1)
assert n1 == 1
c = c.replace(old_remove, new_remove, 1)

old_insert = '''  html += '<button onclick="startNewBlend()" style="width:100%;margin-bottom:16px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">+ New Blend</button>';
  html += '<div class="section-label">Vial details</div>';'''
new_insert = '''  html += '<button onclick="startNewBlend()" style="width:100%;margin-bottom:16px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">+ New Blend</button>';
  html += '<div class="card" style="margin-bottom:12px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter how much bac water you added<br>' +
    '2. Enter each compound\\'s name and amount in the vial<br>' +
    '3. Enter your desired dose for ONE compound \\u2014 the others calculate automatically<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>';
  html += '<div class="section-label">Vial details</div>';'''
n2 = c.count(old_insert)
print("insert count:", n2)
assert n2 == 1
c = c.replace(old_insert, new_insert, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
