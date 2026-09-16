c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  if (!compounds.length) { alert('Enter at least one compound amount first'); return; }

  const name = prompt('Name this blend:');
  if (!name || !name.trim()) return;

  try {
    await POST('/api/saved-calcs/blends', {
      name: name.trim(),
      water: water,
      vial_unit: vialUnit,
      dose_unit: doseUnit,
      compounds: compounds,
    });
    loadSavedBlends();
  } catch (err) { alert(err.message); }'''
new = '''  if (!compounds.length) { alert('Enter at least one compound amount first'); return; }

  let defaultName = '';
  if (BLEND_EDITING_ID) {
    try {
      const existing = await GET('/api/saved-calcs/blends');
      const match = existing.find(function(b) { return b.id === BLEND_EDITING_ID; });
      if (match) defaultName = match.name;
    } catch (err) { /* fall through with blank default */ }
  }

  const name = prompt(BLEND_EDITING_ID ? 'Rename this blend:' : 'Name this blend:', defaultName);
  if (!name || !name.trim()) return;

  const payload = {
    name: name.trim(),
    water: water,
    vial_unit: vialUnit,
    dose_unit: doseUnit,
    compounds: compounds,
  };

  try {
    if (BLEND_EDITING_ID) {
      await PUT('/api/saved-calcs/blends/' + BLEND_EDITING_ID, payload);
    } else {
      await POST('/api/saved-calcs/blends', payload);
    }
    loadSavedBlends();
  } catch (err) { alert(err.message); }'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
