c = open('/home/madfella/peptidetrack/static/app.js').read()
old = 'let BLEND_ANCHOR_ID = null;'
new = 'let BLEND_LAST_EDITED_ID = null;'
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
