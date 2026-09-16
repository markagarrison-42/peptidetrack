c = open('/home/madfella/peptidetrack/static/app.js').read()

old_save = '''async function saveCalcAs() {
  const vial  = parseFloat(document.getElementById('calc-vial').value);
  const water = parseFloat(document.getElementById('calc-water').value);
  const dose  = parseFloat(document.getElementById('calc-dose').value);
  const unit  = document.getElementById('calc-unit') ? document.getElementById('calc-unit').value : 'mg';
  if (!vial || !water || !dose) { alert('Enter vial size, water, and dose first'); return; }
  const name = prompt('Name this calculation:');
  if (!name || !name.trim()) return;
  try {
    await POST('/api/saved-calcs/', { name: name.trim(), vial_size: vial, unit: unit, water: water, dose: dose });
    loadSavedCalcs();
  } catch (err) { alert(err.message); }
}'''
new_save = '''let CALC_LOADED = null;

async function saveCalcAs() {
  const vial  = parseFloat(document.getElementById('calc-vial').value);
  const water = parseFloat(document.getElementById('calc-water').value);
  const dose  = parseFloat(document.getElementById('calc-dose').value);
  const vialUnit = document.getElementById('calc-vial-unit') ? document.getElementById('calc-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('calc-dose-unit') ? document.getElementById('calc-dose-unit').value : 'mg';
  if (!vial || !water || !dose) { alert('Enter vial size, water, and dose first'); return; }
  const defaultName = (CALC_LOADED && CALC_LOADED.vial === vial && CALC_LOADED.water === water && CALC_LOADED.dose === dose && CALC_LOADED.vialUnit === vialUnit && CALC_LOADED.doseUnit === doseUnit) ? CALC_LOADED.name : '';
  const name = prompt('Name this calculation:', defaultName);
  if (!name || !name.trim()) return;
  try {
    await POST('/api/saved-calcs/', { name: name.trim(), vial_size: vial, unit: vialUnit, dose_unit: doseUnit, water: water, dose: dose });
    loadSavedCalcs();
  } catch (err) { alert(err.message); }
}'''
n1 = c.count(old_save)
print("save count:", n1)
assert n1 == 1
c = c.replace(old_save, new_save, 1)

old_load = '''function loadSavedCalc(calcId) {
  GET('/api/saved-calcs/').then(function(calcs) {
    const calc = calcs.find(function(c) { return c.id === calcId; });
    if (!calc) return;
    document.getElementById('calc-vial').value  = calc.vial_size;
    document.getElementById('calc-unit').value  = calc.unit;
    document.getElementById('calc-water').value = calc.water;
    document.getElementById('calc-dose').value  = calc.dose;
    updateCalcLabels();
    runCalc();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}'''
new_load = '''function loadSavedCalc(calcId) {
  GET('/api/saved-calcs/').then(function(calcs) {
    const calc = calcs.find(function(c) { return c.id === calcId; });
    if (!calc) return;
    document.getElementById('calc-vial').value = calc.vial_size;
    document.getElementById('calc-vial-unit').value = calc.unit;
    document.getElementById('calc-water').value = calc.water;
    document.getElementById('calc-dose').value = calc.dose;
    document.getElementById('calc-dose-unit').value = calc.dose_unit || calc.unit;
    CALC_LOADED = { name: calc.name, vial: calc.vial_size, water: calc.water, dose: calc.dose, vialUnit: calc.unit, doseUnit: calc.dose_unit || calc.unit };
    updateCalcLabels();
    runCalc();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}'''
n2 = c.count(old_load)
print("load count:", n2)
assert n2 == 1
c = c.replace(old_load, new_load, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
