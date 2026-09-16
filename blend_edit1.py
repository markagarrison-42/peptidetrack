c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''      html += '<div style="flex:1">';
      html += '<div style="font-size:14px;font-weight:600">' + blend.name + '</div>';
      html += '<div style="font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:2px">' + names + '</div>';
      html += '</div>';
      html += '<button onclick="deleteSavedBlend(' + blend.id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:28px;height:28px;font-size:14px;cursor:pointer;flex-shrink:0;margin-left:8px">\\u2715</button>';'''
new = '''      html += '<div onclick="loadSavedBlend(' + blend.id + ')" style="flex:1;cursor:pointer">';
      html += '<div style="font-size:14px;font-weight:600">' + blend.name + '</div>';
      html += '<div style="font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:2px">' + names + '</div>';
      html += '</div>';
      html += '<button onclick="deleteSavedBlend(' + blend.id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:28px;height:28px;font-size:14px;cursor:pointer;flex-shrink:0;margin-left:8px">\\u2715</button>';'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
