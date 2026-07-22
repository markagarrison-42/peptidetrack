content = open('/home/madfella/peptidetrack/templates/index.html').read()

# Replace circle with rounded rectangle
old = """    .dose-check {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 2px solid var(--border2);
      background: transparent;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;
    }"""

new = """    .dose-check {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      border: 2px solid var(--border2);
      background: transparent;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;
    }"""

if old in content:
    content = content.replace(old, new)
    print('shape changed to rounded rect: OK')
else:
    print('NOT FOUND')

# Also fix checked state to use rounded rect
old_checked = """    .dose-check.checked {
      background: linear-gradient(135deg, #00e5d4, #7c5fe6);
      border-color: transparent;
      box-shadow: 0 0 18px rgba(0,229,212,0.4);
      width: 44px;
      height: 44px;
    }"""

new_checked = """    .dose-check.checked {
      background: linear-gradient(135deg, #00e5d4, #7c5fe6);
      border-color: transparent;
      border-radius: 12px;
      box-shadow: 0 0 14px rgba(0,229,212,0.35);
    }"""

if old_checked in content:
    content = content.replace(old_checked, new_checked)
    print('checked state fixed: OK')
else:
    print('checked NOT FOUND')

# Fix skipped check too
old_skipped = """    .dose-check.skipped-check {
      border-color: var(--border2);
      background: transparent;
    }"""

new_skipped = """    .dose-check.skipped-check {
      border-color: var(--border2);
      background: transparent;
      border-radius: 12px;
    }"""

content = content.replace(old_skipped, new_skipped)

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(content)
print('saved')
