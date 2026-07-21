content = open('/var/www/protocol_mg42apps_com_wsgi.py').read()
print('Before length:', len(content))

# Find and replace the VAPID private key line
lines = content.split('\n')
new_lines = []
for line in lines:
    if 'VAPID_PRIVATE_KEY' in line:
        new_lines.append("os.environ['VAPID_PRIVATE_KEY'] = 'Lg17_ylCBG3YbQxm9fW_J1CpqrhBO6kW3C4ZOcRMJGs'")
        print('Replaced VAPID_PRIVATE_KEY line')
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)
open('/var/www/protocol_mg42apps_com_wsgi.py', 'w').write(content)
print('After length:', len(content))
print('New key:', [l for l in new_lines if 'VAPID_PRIVATE' in l])
