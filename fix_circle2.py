content = open('/home/madfella/peptidetrack/templates/index.html').read()

# Check current state
idx = content.find('.dose-check {')
print('Current .dose-check CSS:')
print(repr(content[idx:idx+300]))

# Find border-radius in dose-check
if 'border-radius: 50%' in content:
    content = content.replace('border-radius: 50%;', 'border-radius: 10px;')
    print('Changed 50% to 10px')
elif 'border-radius: 12px' in content and '.dose-check {' in content:
    print('Already 12px')
else:
    print('border-radius NOT FOUND in dose-check')

open('/home/madfella/peptidetrack/templates/index.html', 'w').write(content)
print('saved')
