c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''    '<div id="calc-result" style="display:none">' +
    '<div class="card"><div class="card-body">' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid var(--border)">' +'''
new = '''    '<div id="calc-result" style="display:none">' +
    '<div class="card"><div class="card-body">' +
    '<div id="calc-loaded-badge" style="display:none;font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-dim);padding:4px 10px;border-radius:6px;margin-bottom:12px"></div>' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid var(--border)">' +'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
