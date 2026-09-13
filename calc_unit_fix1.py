c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

start = None
end = None
for i, l in enumerate(lines):
    if l.startswith('function loadCalc() {'):
        start = i
    if l.startswith('async function loadSavedCalcs() {'):
        end = i
        break

print("start:", start, "end:", end)
assert start is not None and end is not None, "boundaries not found, aborting"
print("old block line count:", end - start)
