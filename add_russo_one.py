c = open('/home/madfella/peptidetrack/templates/index.html').read()
results = []

def patch(label, old, new):
    global c
    n = c.count(old)
    if n == 1:
        c = c.replace(old, new, 1)
        results.append((label, "OK"))
    else:
        results.append((label, f"ABORTED (found {n}, expected 1)"))

patch("font-link",
'''  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">''',
'''  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Russo+One&display=swap" rel="stylesheet">''')

patch("topbar-logo",
'''    #topbar-logo {
      font-family: var(--sans);
      font-size: 17px;''',
'''    #topbar-logo {
      font-family: 'Russo One', var(--sans);
      font-size: 17px;''')

patch("auth-mark",
'''    .auth-mark {
      font-family: var(--sans);
      font-size: 13px;''',
'''    .auth-mark {
      font-family: 'Russo One', var(--sans);
      font-size: 13px;''')

for label, status in results:
    print(f"{label}: {status}")

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(c)
print("--- file written ---")
