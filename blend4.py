c = open('/home/madfella/peptidetrack/static/app.js').read()

old = '''function runBlendCalc() {
  // math built in next step
}'''

new = '''function runBlendCalc() {
  const water = parseFloat(document.getElementById('blend-water').value);
  const vialUnit = document.getElementById('blend-vial-unit') ? document.getElementById('blend-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('blend-dose-unit') ? document.getElementById('blend-dose-unit').value : 'mg';
  const anchorDoseRaw = parseFloat(document.getElementById('blend-dose').value);
  const resultBox = document.getElementById('blend-result');
  const isIU = (vialUnit === 'IU' || doseUnit === 'IU');

  const rows = BLEND_ROW_IDS.map(function(id) {
    return {
      id: id,
      name: (document.getElementById('blend-name-' + id) || {}).value || ('Compound ' + id),
      amount: parseFloat((document.getElementById('blend-amount-' + id) || {}).value),
    };
  });

  const anchorRow = rows.find(function(r) { return r.id === BLEND_ANCHOR_ID; });

  if (!water || water <= 0 || !anchorDoseRaw || anchorDoseRaw <= 0 || !anchorRow || !anchorRow.amount || anchorRow.amount <= 0) {
    if (resultBox) resultBox.style.display = 'none';
    rows.forEach(function(r) {
      const box = document.getElementById('blend-result-' + r.id);
      if (box) box.textContent = '';
    });
    return;
  }

  const anchorAmountMg = isIU ? anchorRow.amount : massToMg(anchorRow.amount, vialUnit);
  const anchorDoseMg   = isIU ? anchorDoseRaw    : massToMg(anchorDoseRaw, doseUnit);
  const anchorConc     = anchorAmountMg / water;
  const drawMl         = anchorDoseMg / anchorConc;
  const drawUnits      = Math.round(drawMl * 100 * 10) / 10;

  rows.forEach(function(r) {
    const box = document.getElementById('blend-result-' + r.id);
    if (!box) return;
    if (!r.amount || r.amount <= 0) { box.textContent = ''; return; }
    if (r.id === BLEND_ANCHOR_ID) {
      box.textContent = 'Anchor \\u00b7 ' + (isIU ? anchorDoseRaw : anchorDoseRaw) + ' ' + doseUnit + ' per draw';
      return;
    }
    const amountMg = isIU ? r.amount : massToMg(r.amount, vialUnit);
    const conc = amountMg / water;
    const resultMg = conc * drawMl;
    const resultDisplay = isIU ? resultMg : mgToUnit(resultMg, doseUnit);
    box.textContent = 'Resulting dose \\u00b7 ' + resultDisplay.toFixed(isIU ? 0 : 2) + ' ' + doseUnit;
  });

  document.getElementById('blend-units').textContent = drawUnits.toFixed(1);
  document.getElementById('blend-volume-line').textContent = drawMl.toFixed(3) + ' mL draw';
  if (resultBox) resultBox.style.display = 'block';
}'''

n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
