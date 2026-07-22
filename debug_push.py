content = open('/home/madfella/peptidetrack/static/app.js').read()
lines = content.split('\n')

# Find the frequency filter block
for i, l in enumerate(lines):
    if "if (item.frequency === 'As needed') return;" in l:
        print(f'Found As needed at line {i+1}')
        # Print context
        for j in range(i-1, i+8):
            print(f'  {j+1}: {repr(lines[j])}')
        break
