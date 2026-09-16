c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''    const unit       = document.getElementById('ac-unit-' + protocolId).value;
    const injectable = ['SubQ', 'IM', 'IV'].includes(route);
    const premixedEl  = document.getElementById('ac-premixed-' + protocolId);
    const isPremixed  = premixedEl ? (premixedEl.value === 'yes') : false;
    const compound   = await POST('/api/compounds/', {
      name, category: 'Other',
      default_route: route, frequency: frequency,
    });
    await POST('/api/protocols/' + protocolId + '/items', {
      compound_id:     compound.id,
      dose_mg:         parseFloat(dose),'''
new = '''    const unit       = document.getElementById('ac-unit-' + protocolId).value;
    const injectable = ['SubQ', 'IM', 'IV'].includes(route);
    const premixedEl  = document.getElementById('ac-premixed-' + protocolId);
    const isPremixed  = premixedEl ? (premixedEl.value === 'yes') : false;
    const doseMgConverted = (unit === 'mcg' || unit === 'g') ? massToMg(parseFloat(dose), unit) : parseFloat(dose);
    const compound   = await POST('/api/compounds/', {
      name, category: 'Other',
      default_route: route, frequency: frequency,
    });
    await POST('/api/protocols/' + protocolId + '/items', {
      compound_id:     compound.id,
      dose_mg:         doseMgConverted,'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
