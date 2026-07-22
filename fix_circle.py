content = open('/home/madfella/peptidetrack/templates/index.html').read()

# Fix: reduce symbol size so circle fill shows properly
old = """    .dose-check.checked .dose-check-symbol {
      color: #07040f;
    }"""
new = """    .dose-check.checked .dose-check-symbol {
      color: #07040f;
      font-size: 16px;
      font-weight: 900;
    }"""
content = content.replace(old, new)

# Also fix base symbol size
old2 = """    .dose-check-symbol {
      font-size: 18px;
      font-weight: 700;
      color: var(--border2);
      line-height: 1;
      transition: color 0.2s;
      font-family: var(--sans);
    }"""
new2 = """    .dose-check-symbol {
      font-size: 16px;
      font-weight: 700;
      color: var(--border2);
      line-height: 1;
      transition: color 0.2s;
      font-family: var(--sans);
      pointer-events: none;
    }"""
content = content.replace(old2, new2)

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(content)
print('circle CSS fixed:', 'pointer-events: none' in content)
