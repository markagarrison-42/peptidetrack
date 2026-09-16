c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

start = None
end = None
for i, l in enumerate(lines):
    if l.startswith('function renderBlendPanel() {'):
        start = i
    if l.startswith('function saveBlendCalcAs() {'):
        end = i
        break

print("start:", start, "end:", end)
assert start is not None and end is not None, "boundaries not found"
print("old block line count:", end - start)
