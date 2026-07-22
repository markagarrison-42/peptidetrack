content = open('/home/madfella/peptidetrack/templates/index.html').read()

# Fix the dose modal input - force dark background
old = """    .dose-modal-input-wrap input {
      flex: 1;
      min-width: 0;
      background: var(--surface);
      border: 1px solid var(--border2);
      border-radius: var(--r);
      color: var(--text);
      font-family: var(--mono);
      font-size: 28px;
      font-weight: 700;
      padding: 16px;
      outline: none;
      text-align: center;
      -webkit-appearance: none;
      appearance: none;
      transition: border-color 0.2s;
    }"""

new = """    .dose-modal-input-wrap input {
      flex: 1;
      min-width: 0;
      background: #0e0a1c !important;
      border: 1px solid var(--border2);
      border-radius: var(--r);
      color: #f0eeff !important;
      font-family: var(--mono);
      font-size: 28px;
      font-weight: 700;
      padding: 16px;
      outline: none;
      text-align: center;
      -webkit-appearance: none;
      appearance: none;
      transition: border-color 0.2s;
      -webkit-text-fill-color: #f0eeff !important;
    }"""

if old in content:
    content = content.replace(old, new)
    print('input CSS fixed: OK')
else:
    print('NOT FOUND - trying partial match')
    idx = content.find('.dose-modal-input-wrap input {')
    if idx >= 0:
        print('Found at:', idx)
        print(repr(content[idx:idx+400]))

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(content)
print('saved')
