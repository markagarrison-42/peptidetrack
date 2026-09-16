c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  html += '<div id="blend-result" style="display:none">';
  html += '<div class="card"><div class="card-body">';
  html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
  html += '<div style="font-size:16px;font-weight:700">Draw</div>';'''
new = '''  html += '<div id="blend-result" style="display:none">';
  html += '<div class="card"><div class="card-body">';
  html += '<div id="blend-loaded-badge" style="display:none;font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-dim);padding:4px 10px;border-radius:6px;margin-bottom:12px"></div>';
  html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
  html += '<div style="font-size:16px;font-weight:700">Draw</div>';'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
