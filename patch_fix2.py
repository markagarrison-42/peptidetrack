content = open('/home/madfella/peptidetrack/static/app.js').read()

# 1. Fix duplicate "As needed" - remove the extra one
old_dup = """      if (item.frequency === 'As needed') return;
      if (item.frequency === 'As needed') return;"""
new_single = "      if (item.frequency === 'As needed') return;"
if old_dup in content:
    content = content.replace(old_dup, new_single)
    print('Duplicate As needed: FIXED')
else:
    print('No duplicate found')

# 2. Fix history date group - find exact string
idx = content.find('history-date-group')
if idx >= 0:
    print('Found history-date-group at:', idx)
    print(repr(content[idx-10:idx+200]))
else:
    print('history-date-group NOT FOUND')

open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
