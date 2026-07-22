content = open('/home/madfella/peptidetrack/static/app.js').read()
lines = content.split('\n')

# Insert allItems.push before line 577 (index 576)
lines.insert(576, "      allItems.push({ item: item, protoName: proto.name });")

content = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)

# Verify
import subprocess
result = subprocess.run(['node', '--check', '/home/madfella/peptidetrack/static/app.js'], capture_output=True, text=True)
if result.returncode == 0:
    print('JS VALID')
    # Confirm the fix
    lines2 = content.split('\n')
    for i in range(574, 582):
        print(f'{i+1}: {repr(lines2[i])}')
else:
    print('JS INVALID:', result.stderr[:200])
