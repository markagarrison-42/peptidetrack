c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  html += '</div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';
  html += '<div id="saved-blends-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">No saved blends yet.</div></div>';
  html += '</div>';'''
new = '''  html += '</div>';
  html += '<div class="card" style="margin-top:4px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter how much bac water you added<br>' +
    '2. Enter each compound\\'s name and amount in the vial<br>' +
    '3. Enter your desired dose for ONE compound \\u2014 the others calculate automatically<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';
  html += '<div id="saved-blends-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">No saved blends yet.</div></div>';
  html += '</div>';'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
