content = open('/home/madfella/peptidetrack/static/app.js').read()
lines = content.split('\n')

# Find both renderUnscheduledSection calls
unsched_lines = [i for i,l in enumerate(lines) if 'renderUnscheduledSection' in l]
print('renderUnscheduledSection at lines:', [i+1 for i in unsched_lines])

# Find both tomorrow sections
tomorrow_lines = [i for i,l in enumerate(lines) if '// Tomorrow\'s schedule' in l]
print('Tomorrow sections at lines:', [i+1 for i in tomorrow_lines])

# Find end of second tomorrow section (ends with el.innerHTML = html;)
if len(tomorrow_lines) >= 2:
    second_start = tomorrow_lines[1] - 1  # Include the blank line before
    # Find el.innerHTML = html; after second tomorrow
    for i in range(second_start, len(lines)):
        if 'el.innerHTML = html;' in lines[i]:
            second_end = i
            break
    print(f'Removing lines {second_start+1} to {second_end+1}')
    # Remove the second tomorrow section and second renderUnscheduledSection
    # Also need to remove duplicate renderUnscheduledSection
    # The second tomorrow block starts at tomorrow_lines[1]-1 and ends at second_end
    del lines[second_start:second_end+1]
    print('Second tomorrow removed')

# Now check renderUnscheduledSection - should only be one
content = '\n'.join(lines)
unsched = [i for i,l in enumerate(content.split('\n')) if 'renderUnscheduledSection' in l]
print('renderUnscheduledSection after fix:', [i+1 for i in unsched])

import subprocess
open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
result = subprocess.run(['node', '--check', '/home/madfella/peptidetrack/static/app.js'], capture_output=True, text=True)
print('JS:', 'VALID' if result.returncode == 0 else 'INVALID: ' + result.stderr[:200])
