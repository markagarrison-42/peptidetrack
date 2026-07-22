content = open('/home/madfella/peptidetrack/static/app.js').read()

# Add a helper function to format time as 12hr
# Insert after the fmtDateShort function
old_fmt = "function fmtNum(n, dec) {"
new_fmt = """function fmt12hr(hhmm) {
  if (!hhmm) return hhmm;
  var parts = hhmm.split(':');
  var h = parseInt(parts[0]);
  var m = parts[1];
  var ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return h + ':' + m + ' ' + ampm;
}

function fmtNum(n, dec) {"""

if old_fmt in content:
    content = content.replace(old_fmt, new_fmt)
    print('fmt12hr added: OK')
else:
    print('fmtNum NOT FOUND')

# Replace all reminder_time display with fmt12hr
# In renderProtocolCard compound display
content = content.replace(
    "if (item.reminder_time) html += ' · 🔔 ' + item.reminder_time;",
    "if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);"
)

# In renderToday dose cards
content = content.replace(
    "if (item.reminder_time) html += ' · 🔔 ' + item.reminder_time;",
    "if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);"
)

# In tomorrow section
content = content.replace(
    "if (item.reminder_time) html += ' · 🔔 ' + item.reminder_time;",
    "if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);"
)

print('All reminder_time displays updated')

import subprocess
result = subprocess.run(['node', '--check', '/home/madfella/peptidetrack/static/app.js'], capture_output=True, text=True)
if result.returncode != 0:
    print('JS INVALID:', result.stderr[:200])
    # Don't save if invalid
else:
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
    print('JS VALID - saved')
