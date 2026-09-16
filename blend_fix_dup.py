c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

assert lines[2483] == 'function saveBlendCalcAs() {', "line 2483 mismatch: " + repr(lines[2483])
assert lines[2484] == 'function saveBlendCalcAs() {', "line 2484 mismatch: " + repr(lines[2484])

del lines[2483]
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
