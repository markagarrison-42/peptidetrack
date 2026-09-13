c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

target1 = '   ONBOARDING'
target2 = '══════════════════════════════════════════ */'

idx = None
for i in range(len(lines) - 1):
    if lines[i].strip() == target1.strip() and lines[i+1].strip() == target2.strip():
        idx = i
        break

print("found orphan fragment at:", idx)
assert idx is not None, "orphan fragment not found, aborting"

del lines[idx:idx+2]
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
