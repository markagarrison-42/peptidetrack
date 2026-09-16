c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

start = None
end = None
for i, l in enumerate(lines):
    if l.startswith('function renderBlendPanel() {'):
        start = i
    if l.startswith('function saveBlendCalcAs() {'):
        end = i
        break

assert start == 2324 and end == 2470, "boundaries shifted, aborting"

new_block = '''function renderBlendPanel() {
  BLEND_ROW_IDS = [1, 2];
  BLEND_NEXT_ID = 3;
  BLEND_LAST_EDITED_ID = 1;
  let html = '<div class="section" style="padding:20px">';
  html += '<div class="section-label">Vial details</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Water (mL)</label><input type="number" id="blend-water" step="0.1" inputmode="decimal" placeholder="3" oninput="runBlendCalc()"></div>';
  html += '<div class="field-row"><div class="field" style="flex:1"><label>Vial amount unit</label><select id="blend-vial-unit" onchange="syncBlendUnits(\\'vial\\');runBlendCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div></div>';
  html += '<div id="blend-vial-rows">';
  BLEND_ROW_IDS.forEach(function(id, idx) { html += renderBlendVialRowHtml(id, idx); });
  html += '</div>';
  html += '<button onclick="addBlendRow()" style="width:100%;margin-top:8px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">+ Add compound</button>';
  html += '</div></div>';
  html += '<div class="section-label" style="margin-top:20px">Amount desired</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field-row"><div class="field" style="flex:1"><label>Unit</label><select id="blend-dose-unit" onchange="syncBlendUnits(\\'dose\\');runBlendCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div></div>';
  html += '<div id="blend-dose-rows">';
  BLEND_ROW_IDS.forEach(function(id, idx) { html += renderBlendDoseRowHtml(id, idx); });
  html += '</div>';
  html += '</div></div>';
  html += '<div id="blend-result" style="display:none">';
  html += '<div class="card"><div class="card-body">';
  html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
  html += '<div style="font-size:16px;font-weight:700">Draw</div>';
  html += '<div style="font-family:var(--mono);font-size:22px;font-weight:700;color:var(--accent)"><span id="blend-units">\\u2014</span> Units</div>';
  html += '</div>';
  html += '<div style="font-family:var(--mono);font-size:12px;color:var(--muted)" id="blend-volume-line">\\u2014</div>';
  html += '<div style="font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:4px">Vial contains <span id="blend-doses-total" style="color:var(--green);font-weight:700">\\u2014</span> doses</div>';
  html += '<button onclick="saveBlendCalcAs()" style="width:100%;margin-top:12px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">Save As...</button>';
  html += '</div></div>';
  html += '</div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';
  html += '<div id="saved-blends-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">No saved blends yet.</div></div>';
  html += '</div>';
  return html;
}

const BLEND_DOT_COLORS = ['#f0a83c', '#4a9eff', '#00e5d4', '#ff6ba8', '#a78bfa', '#ff8c66'];

function renderBlendVialRowHtml(id, idx) {
  const color = BLEND_DOT_COLORS[idx % BLEND_DOT_COLORS.length];
  return '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px" id="blend-vial-row-' + id + '">' +
    '<div style="width:14px;height:14px;border-radius:50%;background:' + color + ';flex-shrink:0"></div>' +
    '<input type="text" id="blend-name-' + id + '" placeholder="Compound name" oninput="renderBlendDoseRows();runBlendCalc()" style="flex:1;background:var(--bg);border:1px solid var(--border2);border-radius:8px;padding:10px 12px;color:var(--text);font-family:var(--sans);font-size:14px">' +
    '<input type="number" id="blend-amount-' + id + '" step="0.01" inputmode="decimal" placeholder="5" oninput="runBlendCalc()" style="width:80px;background:var(--bg);border:1px solid var(--border2);border-radius:8px;padding:10px 12px;color:var(--text);font-family:var(--mono);font-size:14px">' +
    '<button onclick="removeBlendRow(' + id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:36px;height:36px;font-size:14px;cursor:pointer;flex-shrink:0">\\u2715</button>' +
    '</div>';
}

function renderBlendDoseRowHtml(id, idx) {
  const color = BLEND_DOT_COLORS[idx % BLEND_DOT_COLORS.length];
  const nameInput = document.getElementById('blend-name-' + id);
  const name = (nameInput && nameInput.value.trim()) ? nameInput.value.trim() : ('Compound ' + id);
  return '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px" id="blend-dose-row-' + id + '">' +
    '<div style="width:14px;height:14px;border-radius:50%;background:' + color + ';flex-shrink:0"></div>' +
    '<div style="flex:1;font-size:14px;color:var(--text)">' + name + '</div>' +
    '<input type="number" id="blend-desired-' + id + '" step="0.01" inputmode="decimal" placeholder="150" oninput="setBlendLastEdited(' + id + ');runBlendCalc()" style="width:100px;background:var(--bg);border:1px solid var(--border2);border-radius:8px;padding:10px 12px;color:var(--text);font-family:var(--mono);font-size:14px">' +
    '</div>';
}

function renderBlendDoseRows() {
  const container = document.getElementById('blend-dose-rows');
  if (!container) return;
  const preserved = {};
  BLEND_ROW_IDS.forEach(function(id) {
    const el = document.getElementById('blend-desired-' + id);
    if (el) preserved[id] = el.value;
  });
  container.innerHTML = BLEND_ROW_IDS.map(function(id, idx) { return renderBlendDoseRowHtml(id, idx); }).join('');
  BLEND_ROW_IDS.forEach(function(id) {
    const el = document.getElementById('blend-desired-' + id);
    if (el && preserved[id] !== undefined) el.value = preserved[id];
  });
}

function addBlendRow() {
  const id = BLEND_NEXT_ID++;
  BLEND_ROW_IDS.push(id);
  const vialContainer = document.getElementById('blend-vial-rows');
  if (vialContainer) vialContainer.insertAdjacentHTML('beforeend', renderBlendVialRowHtml(id, BLEND_ROW_IDS.length - 1));
  renderBlendDoseRows();
}

function removeBlendRow(id) {
  if (BLEND_ROW_IDS.length <= 1) return;
  BLEND_ROW_IDS = BLEND_ROW_IDS.filter(function(x) { return x !== id; });
  const vRow = document.getElementById('blend-vial-row-' + id);
  if (vRow) vRow.remove();
  if (BLEND_LAST_EDITED_ID === id) BLEND_LAST_EDITED_ID = BLEND_ROW_IDS[0];
  renderBlendDoseRows();
  runBlendCalc();
}

function setBlendLastEdited(id) {
  BLEND_LAST_EDITED_ID = id;
}

function syncBlendUnits(changed) {
  const vialSel = document.getElementById('blend-vial-unit');
  const doseSel = document.getElementById('blend-dose-unit');
  if (!vialSel || !doseSel) return;
  if (changed === 'vial' && vialSel.value === 'IU') doseSel.value = 'IU';
  if (changed === 'dose' && doseSel.value === 'IU') vialSel.value = 'IU';
}

function runBlendCalc() {
  const water = parseFloat(document.getElementById('blend-water').value);
  const vialUnit = document.getElementById('blend-vial-unit') ? document.getElementById('blend-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('blend-dose-unit') ? document.getElementById('blend-dose-unit').value : 'mg';
  const resultBox = document.getElementById('blend-result');
  const isIU = (vialUnit === 'IU' || doseUnit === 'IU');

  const rows = BLEND_ROW_IDS.map(function(id) {
    return {
      id: id,
      amount: parseFloat((document.getElementById('blend-amount-' + id) || {}).value),
    };
  });

  const anchorRow = rows.find(function(r) { return r.id === BLEND_LAST_EDITED_ID; });
  const anchorDoseEl = document.getElementById('blend-desired-' + BLEND_LAST_EDITED_ID);
  const anchorDoseRaw = anchorDoseEl ? parseFloat(anchorDoseEl.value) : NaN;

  if (!water || water <= 0 || !anchorDoseRaw || anchorDoseRaw <= 0 || !anchorRow || !anchorRow.amount || anchorRow.amount <= 0) {
    if (resultBox) resultBox.style.display = 'none';
    return;
  }

  const anchorAmountMg = isIU ? anchorRow.amount : massToMg(anchorRow.amount, vialUnit);
  const anchorDoseMg   = isIU ? anchorDoseRaw    : massToMg(anchorDoseRaw, doseUnit);
  const anchorConc     = anchorAmountMg / water;
  const drawMl         = anchorDoseMg / anchorConc;
  const drawUnits      = Math.round(drawMl * 100 * 10) / 10;

  let minDoses = Infinity;

  rows.forEach(function(r) {
    if (!r.amount || r.amount <= 0) return;
    const amountMg = isIU ? r.amount : massToMg(r.amount, vialUnit);
    const conc = amountMg / water;
    const resultMg = conc * drawMl;
    const resultDisplay = isIU ? resultMg : mgToUnit(resultMg, doseUnit);

    if (r.id !== BLEND_LAST_EDITED_ID) {
      const el = document.getElementById('blend-desired-' + r.id);
      if (el) el.value = resultDisplay.toFixed(isIU ? 0 : 2);
    }

    const dosesForThis = amountMg / resultMg;
    if (dosesForThis < minDoses) minDoses = dosesForThis;
  });

  document.getElementById('blend-units').textContent = drawUnits.toFixed(1);
  document.getElementById('blend-volume-line').textContent = drawMl.toFixed(3) + ' mL draw';
  document.getElementById('blend-doses-total').textContent = isFinite(minDoses) ? minDoses.toFixed(2) : '\\u2014';
  if (resultBox) resultBox.style.display = 'block';
}

function saveBlendCalcAs() {'''.split('\n')

lines[start:end] = new_block
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
