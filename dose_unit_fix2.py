c = open('/home/madfella/peptidetrack/templates/index.html').read()
old = '''      <input type="number" id="ecm-dose" inputmode="decimal" step="0.01" placeholder="0">
      <span class="dose-modal-unit" id="ecm-unit">mg</span>'''
new = '''      <input type="number" id="ecm-dose" inputmode="decimal" step="0.01" placeholder="0">
      <select class="dose-modal-unit" id="ecm-unit" onchange="updateEcmDoseDisplay()"><option>mg</option><option>mcg</option><option>IU</option><option>mL</option><option>g</option></select>'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/templates/index.html', 'w').write(c)
print("written")
