c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  if (isNaN(dose) || dose <= 0) { flash('ecm-flash', 'Enter a valid dose', true); return; }
  var premixedSel = document.getElementById('ecm-premixed');'''
new = '''  if (isNaN(dose) || dose <= 0) { flash('ecm-flash', 'Enter a valid dose', true); return; }
  const ecmUnit = document.getElementById('ecm-unit') ? document.getElementById('ecm-unit').value : 'mg';
  const doseMgConverted = (ecmUnit === 'mcg' || ecmUnit === 'g') ? massToMg(dose, ecmUnit) : dose;
  var premixedSel = document.getElementById('ecm-premixed');'''
n1 = c.count(old)
print("var count:", n1)
assert n1 == 1
c = c.replace(old, new, 1)

old2 = '''    await PUT('/api/protocols/items/' + itemId, {
      dose_mg:         dose,'''
new2 = '''    await PUT('/api/protocols/items/' + itemId, {
      dose_mg:         doseMgConverted,
      notes:           ecmUnit !== 'mg' ? 'unit:' + ecmUnit : null,'''
n2 = c.count(old2)
print("put count:", n2)
assert n2 == 1
c = c.replace(old2, new2, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
