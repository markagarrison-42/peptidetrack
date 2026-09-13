c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

start = None
end = None
for i, l in enumerate(lines):
    if l.startswith('function loadCalc() {'):
        start = i
    if l.startswith('async function loadSavedCalcs() {'):
        end = i
        break

assert start == 2254 and end == 2320, "boundaries shifted since last check, aborting"

new_block = '''function loadCalc() {
  const el = document.getElementById('page-calc');
  el.innerHTML =
    safetyBanner() +
    '<div class="section">' +
    '<div class="section-label">Reconstitution calculator</div>' +
    '<div class="card"><div class="card-body">' +
    '<div class="field-row">' +
    '<div class="field" style="flex:2"><label id="calc-vial-label">Vial size (mg)</label>' +
    '<input type="number" id="calc-vial" step="0.1" inputmode="decimal" placeholder="5" oninput="runCalc()"></div>' +
    '<div class="field" style="flex:1"><label>Unit</label>' +
    '<select id="calc-vial-unit" onchange="syncCalcUnits(\\'vial\\');updateCalcLabels();runCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div>' +
    '</div>' +
    '<div class="field"><label>Bacteriostatic water added (mL)</label>' +
    '<input type="number" id="calc-water" step="0.1" inputmode="decimal" placeholder="2" oninput="runCalc()"></div>' +
    '<div class="field-row">' +
    '<div class="field" style="flex:2"><label id="calc-dose-label">Desired dose (mg)</label>' +
    '<input type="number" id="calc-dose" step="0.01" inputmode="decimal" placeholder="0.5" oninput="runCalc()"></div>' +
    '<div class="field" style="flex:1"><label>Unit</label>' +
    '<select id="calc-dose-unit" onchange="syncCalcUnits(\\'dose\\');updateCalcLabels();runCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div>' +
    '</div>' +
    '</div></div>' +
    '<div id="calc-result" style="display:none">' +
    '<div class="card"><div class="card-body">' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid var(--border)">' +
    '<div><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Concentration</div>' +
    '<div style="font-family:var(--mono);font-size:22px;font-weight:700" id="calc-conc">\\u2014</div></div>' +
    '<div style="text-align:right"><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Volume</div>' +
    '<div style="font-family:var(--mono);font-size:22px;font-weight:700" id="calc-ml">\\u2014</div></div>' +
    '</div>' +
    '<div style="text-align:center;padding:16px 0">' +
    '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:10px">Draw to this line on insulin syringe</div>' +
    '<div style="font-family:var(--mono);font-size:56px;font-weight:700;color:var(--accent);line-height:1" id="calc-units">\\u2014</div>' +
    '<div style="font-family:var(--mono);font-size:16px;color:var(--muted);margin-top:4px">units</div>' +
    '</div>' +
    '<div style="display:flex;justify-content:center;padding:12px 0 4px;border-top:1px solid var(--border);margin-top:8px">' +
    '<div style="text-align:center">' +
    '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Doses per vial</div>' +
    '<div style="font-family:var(--mono);font-size:36px;font-weight:700;color:var(--green);line-height:1" id="calc-doses">\\u2014</div>' +
    '<div style="font-family:var(--mono);font-size:14px;color:var(--muted);margin-top:4px">doses</div>' +
    '</div></div>' +
    '<button onclick="saveCalcAs()" style="width:100%;margin-top:12px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">Save As...</button>' +
    '</div></div></div>' +
    '<div class="card" style="margin-top:4px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter your vial size (printed on the vial)<br>' +
    '2. Enter how much bac water you added<br>' +
    '3. Enter your prescribed dose<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>' +
    '<div class="section-label" style="margin-top:20px">Saved calculations</div>' +
    '<div id="saved-calcs-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">Loading...</div></div>' +
    '</div>';
  loadSavedCalcs();
}

function syncCalcUnits(changed) {
  const vialSel = document.getElementById('calc-vial-unit');
  const doseSel = document.getElementById('calc-dose-unit');
  if (!vialSel || !doseSel) return;
  if (changed === 'vial' && vialSel.value === 'IU') doseSel.value = 'IU';
  if (changed === 'dose' && doseSel.value === 'IU') vialSel.value = 'IU';
}

function massToMg(value, unit) {
  if (unit === 'mcg') return value / 1000;
  if (unit === 'g') return value * 1000;
  return value;
}

function mgToUnit(mgValue, unit) {
  if (unit === 'mcg') return mgValue * 1000;
  if (unit === 'g') return mgValue / 1000;
  return mgValue;
}

function updateCalcLabels() {
  const vialUnit = document.getElementById('calc-vial-unit') ? document.getElementById('calc-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('calc-dose-unit') ? document.getElementById('calc-dose-unit').value : 'mg';
  const vl = document.getElementById('calc-vial-label');
  const dl = document.getElementById('calc-dose-label');
  if (vl) vl.textContent = 'Vial size (' + vialUnit + ')';
  if (dl) dl.textContent = 'Desired dose (' + doseUnit + ')';
}

function runCalc() {
  const vial  = parseFloat(document.getElementById('calc-vial').value);
  const water = parseFloat(document.getElementById('calc-water').value);
  const dose  = parseFloat(document.getElementById('calc-dose').value);
  const res   = document.getElementById('calc-result');
  const vialUnit = document.getElementById('calc-vial-unit') ? document.getElementById('calc-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('calc-dose-unit') ? document.getElementById('calc-dose-unit').value : 'mg';

  if (!vial || !water || !dose || water <= 0 || vial <= 0 || dose <= 0) {
    if (res) res.style.display = 'none';
    return;
  }

  const isIU = (vialUnit === 'IU' || doseUnit === 'IU');
  let vialMg, doseMg;
  if (isIU) {
    vialMg = vial;
    doseMg = dose;
  } else {
    vialMg = massToMg(vial, vialUnit);
    doseMg = massToMg(dose, doseUnit);
  }

  const concMgPerMl = vialMg / water;
  const ml = doseMg / concMgPerMl;
  const units = Math.round(ml * 100 * 10) / 10;
  const dosesInVial = Math.floor(vialMg / doseMg);

  const concDisplay = isIU ? concMgPerMl : mgToUnit(concMgPerMl, doseUnit);
  const concUnitLabel = isIU ? 'IU' : doseUnit;

  document.getElementById('calc-conc').textContent  = concDisplay.toFixed(concUnitLabel === 'IU' ? 0 : 2) + ' ' + concUnitLabel + '/mL';
  document.getElementById('calc-ml').textContent    = ml.toFixed(3) + ' mL';
  document.getElementById('calc-units').textContent = units.toFixed(1);
  document.getElementById('calc-doses').textContent = dosesInVial;
  res.style.display = 'block';
}

'''.split('\n')

lines[start:end] = new_block
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
