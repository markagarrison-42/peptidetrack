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

patch("unscheduled-toggle",
'''    .unscheduled-toggle {
      width: 28px;
      height: 28px;''',
'''    .unscheduled-toggle {
      width: 40px;
      height: 40px;''')

patch("skip-btn",
'''    .skip-btn {
      flex-shrink: 0;
      padding: 6px 12px;''',
'''    .skip-btn {
      flex-shrink: 0;
      padding: 11px 16px;
      min-height: 44px;''')

patch("day-btn",
'''    .day-btn {
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--border2);
      background: transparent;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      min-width: 44px;''',
'''    .day-btn {
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--border2);
      background: transparent;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      min-width: 44px;
      min-height: 44px;''')

for label, status in results:
    print(f"{label}: {status}")

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(c)
print("--- file written ---")
