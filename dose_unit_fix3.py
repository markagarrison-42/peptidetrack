c = open('/home/madfella/peptidetrack/static/app.js').read()

old1 = '''function showEditCompoundModal(itemId, name, dose, unit, frequency, route, timing, vialSize, reconVol, foundItem, currentProtocolId) {
  const modal = document.getElementById('edit-compound-modal');
  document.getElementById('ecm-item-id').value    = itemId;
  document.getElementById('ecm-name').textContent = name;
  document.getElementById('ecm-dose').value       = dose;
  document.getElementById('ecm-unit').textContent = unit;'''
new1 = '''let ECM_TRUE_MG = null;

function showEditCompoundModal(itemId, name, dose, unit, frequency, route, timing, vialSize, reconVol, foundItem, currentProtocolId) {
  const modal = document.getElementById('edit-compound-modal');
  document.getElementById('ecm-item-id').value    = itemId;
  document.getElementById('ecm-name').textContent = name;
  ECM_TRUE_MG = dose;
  const ecmUnitSel = document.getElementById('ecm-unit');
  if (ecmUnitSel) ecmUnitSel.value = unit;
  const ecmDoseDisplay = (unit === 'mcg' || unit === 'g') ? mgToUnit(dose, unit) : dose;
  document.getElementById('ecm-dose').value = ecmDoseDisplay;'''
n1 = c.count(old1)
print("modal count:", n1)
assert n1 == 1
c = c.replace(old1, new1, 1)

anchor2 = "function toggleEcmPremixed() {"
new2 = '''function updateEcmDoseDisplay() {
  const unitSel = document.getElementById('ecm-unit');
  const doseInput = document.getElementById('ecm-dose');
  if (!unitSel || !doseInput || ECM_TRUE_MG === null) return;
  const unit = unitSel.value;
  doseInput.value = (unit === 'mcg' || unit === 'g') ? mgToUnit(ECM_TRUE_MG, unit) : ECM_TRUE_MG;
}

function toggleEcmPremixed() {'''
n2 = c.count(anchor2)
print("fn count:", n2)
assert n2 == 1
c = c.replace(anchor2, new2, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
