c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

update_starts = [i for i, l in enumerate(lines) if l.startswith('function updateCalcLabels() {')]
runcalc_starts = [i for i, l in enumerate(lines) if l.startswith('function runCalc() {')]
print("updateCalcLabels found at:", update_starts)
print("runCalc found at:", runcalc_starts)
assert len(update_starts) == 2 and len(runcalc_starts) == 2, "expected exactly 2 of each, aborting"

start = update_starts[1]
end = None
for i in range(start, len(lines)):
    if 'ONBOARDING' in lines[i]:
        end = i
        break
print("removing lines", start, "to", end)
assert end is not None, "ONBOARDING marker not found, aborting"

removed = lines[start:end]
print("--- first 3 lines of removed block ---")
print('\n'.join(removed[:3]))
print("--- last 3 lines of removed block ---")
print('\n'.join(removed[-3:]))

del lines[start:end]
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
