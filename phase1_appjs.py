c = open('/home/madfella/peptidetrack/static/app.js').read()
results = []

def patch(label, old, new):
    global c
    n = c.count(old)
    if n == 1:
        c = c.replace(old, new, 1)
        results.append((label, "OK"))
    else:
        results.append((label, f"ABORTED (found {n}, expected 1)"))

patch("reorder-up-arrow",
  '''html += '<button onclick="moveProtocol(' + proto.id + ', \\'up\\')" style="background:transparent;border:1px solid var(--border2);border-radius:4px;color:var(--muted);width:28px;height:28px;font-size:13px;cursor:pointer"' + (idx === 0 ? ' disabled' : '') + '>\\u2191</button>';''',
  '''html += '<button onclick="moveProtocol(' + proto.id + ', \\'up\\')" style="background:transparent;border:1px solid var(--border2);border-radius:4px;color:var(--muted);width:40px;height:40px;font-size:15px;cursor:pointer"' + (idx === 0 ? ' disabled' : '') + '>\\u2191</button>';''')

patch("reorder-down-arrow",
  '''html += '<button onclick="moveProtocol(' + proto.id + ', \\'down\\')" style="background:transparent;border:1px solid var(--border2);border-radius:4px;color:var(--muted);width:28px;height:28px;font-size:13px;cursor:pointer"' + (idx === total - 1 ? ' disabled' : '') + '>\\u2193</button>';''',
  '''html += '<button onclick="moveProtocol(' + proto.id + ', \\'down\\')" style="background:transparent;border:1px solid var(--border2);border-radius:4px;color:var(--muted);width:40px;height:40px;font-size:15px;cursor:pointer"' + (idx === total - 1 ? ' disabled' : '') + '>\\u2193</button>';''')

patch("delete-saved-calc",
  '''html += '<button onclick="deleteSavedCalc(' + calc.id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:28px;height:28px;font-size:14px;cursor:pointer;flex-shrink:0;margin-left:8px">\\u2715</button>';''',
  '''html += '<button onclick="deleteSavedCalc(' + calc.id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:40px;height:40px;font-size:16px;cursor:pointer;flex-shrink:0;margin-left:8px">\\u2715</button>';''')

patch("active-paused-toggle",
  '''html += '<button onclick="toggleProtocolActive(' + proto.id + ', ' + patientId + ')" style="padding:5px 12px;border-radius:6px;border:1px solid var(--border2);background:' + (isActive ? 'var(--accent)' : 'transparent') + ';color:' + (isActive ? '#080f1a' : 'var(--muted)') + ';font-family:var(--mono);font-size:11px;font-weight:700;cursor:pointer">' + (isActive ? 'ACTIVE' : 'PAUSED') + '</button>';''',
  '''html += '<button onclick="toggleProtocolActive(' + proto.id + ', ' + patientId + ')" style="padding:11px 16px;border-radius:6px;border:1px solid var(--border2);background:' + (isActive ? 'var(--accent)' : 'transparent') + ';color:' + (isActive ? '#080f1a' : 'var(--muted)') + ';font-family:var(--mono);font-size:11px;font-weight:700;cursor:pointer">' + (isActive ? 'ACTIVE' : 'PAUSED') + '</button>';''')

patch("edit-protocol",
  '''html += '<button onclick="editProtocolName(' + proto.id + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:12px;cursor:pointer">Edit</button>';''',
  '''html += '<button onclick="editProtocolName(' + proto.id + ')" style="padding:11px 14px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:12px;cursor:pointer">Edit</button>';''')

patch("delete-protocol",
  '''html += '<button onclick="deleteProtocolPrompt(' + proto.id + ', \\'' + proto.name.replace(/'/g, "\\\\'") + '\\')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-family:var(--sans);font-size:12px;cursor:pointer">Delete</button>';''',
  '''html += '<button onclick="deleteProtocolPrompt(' + proto.id + ', \\'' + proto.name.replace(/'/g, "\\\\'") + '\\')" style="padding:11px 14px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-family:var(--sans);font-size:12px;cursor:pointer">Delete</button>';''')

patch("edit-compound",
  '''html += '<button onclick="editCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-size:12px;cursor:pointer">Edit</button>';''',
  '''html += '<button onclick="editCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:11px 14px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-size:12px;cursor:pointer">Edit</button>';''')

patch("remove-compound",
  '''html += '<button onclick="removeCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-size:12px;cursor:pointer">\\u2715</button>';''',
  '''html += '<button onclick="removeCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:11px 14px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-size:12px;cursor:pointer">\\u2715</button>';''')

patch("inline-day-btn-minheight",
  '''html += '<button type="button" id="ac-day-' + protocolId + '-' + d + '" data-day="' + d + '" onclick="toggleDayBtn(this)" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--mono);font-size:12px;cursor:pointer;transition:all 0.15s;min-width:44px">' + d + '</button>';''',
  '''html += '<button type="button" id="ac-day-' + protocolId + '-' + d + '" data-day="' + d + '" onclick="toggleDayBtn(this)" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--mono);font-size:12px;cursor:pointer;transition:all 0.15s;min-width:44px;min-height:44px">' + d + '</button>';''')

for label, status in results:
    print(f"{label}: {status}")

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("--- file written ---")
