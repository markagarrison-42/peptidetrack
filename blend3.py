c = open('/home/madfella/peptidetrack/static/app.js').read()

old = '''    '<div class="section" style="padding:20px"><div style="font-size:13px;color:var(--muted)">Blend calculator coming up</div></div>' +'''

new = '''    renderBlendPanel() +'''

n = c.count(old)
print("placeholder swap count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)

anchor2 = "function switchCalcTab(name, btn) {"
functions = '''let BLEND_ROW_IDS = [];
let BLEND_NEXT_ID = 1;
let BLEND_ANCHOR_ID = null;

function renderBlendPanel() {
  BLEND_ROW_IDS = [1, 2];
  BLEND_NEXT_ID = 3;
  BLEND_ANCHOR_ID = 1;
  let html = '<div class="section" style="padding:20px">';
  html += '<div class="section-label">Blend calculator</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field-row">';
  html += '<div class="field" style="flex:1"><label>Vial amount unit</label><select id="blend-vial-unit" onchange="syncBlendUnits(\\'vial\\');runBlendCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div>';
  html += '<div class="field" style="flex:1"><label>Dose unit</label><select id="blend-dose-unit" onchange="syncBlendUnits(\\'dose\\');runBlendCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div>';
  html += '</div>';
  html += '<div class="field"><label>Bacteriostatic water added (mL)</label><input type="number" id="blend-water" step="0.1" inputmode="decimal" placeholder="3" oninput="runBlendCalc()"></div>';
  html += '</div></div>';
  html += '<div class="section-label" style="margin-top:20px">Compounds</div>';
  html += '<div id="blend-rows">';
  BLEND_ROW_IDS.forEach(function(id) { html += renderBlendRowHtml(id); });
  html += '</div>';
  html += '<button onclick="addBlendRow()" style="width:100%;margin-bottom:16px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">+ Add compound</button>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label id="blend-dose-label">Desired dose</label><input type="number" id="blend-dose" step="0.01" inputmode="decimal" placeholder="150" oninput="runBlendCalc()"></div>';
  html += '</div></div>';
  html += '<div id="blend-result" style="display:none">';
  html += '<div class="card"><div class="card-body">';
  html += '<div style="text-align:center;padding:16px 0">';
  html += '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:10px">Draw to this line on insulin syringe</div>';
  html += '<div style="font-family:var(--mono);font-size:56px;font-weight:700;color:var(--accent);line-height:1" id="blend-units">\\u2014</div>';
  html += '<div style="font-family:var(--mono);font-size:16px;color:var(--muted);margin-top:4px">units</div>';
  html += '</div>';
  html += '<div style="font-family:var(--mono);font-size:13px;color:var(--muted);text-align:center;margin-bottom:12px" id="blend-volume-line">\\u2014</div>';
  html += '<button onclick="saveBlendCalcAs()" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--accent);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">Save As...</button>';
  html += '</div></div>';
  html += '</div>';
  html += '<div class="section-label" style="margin-top:20px">Saved blends</div>';
  html += '<div id="saved-blends-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">No saved blends yet.</div></div>';
  html += '</div>';
  return html;
}

function renderBlendRowHtml(id) {
  const checked = (id === BLEND_ANCHOR_ID) ? 'checked' : '';
  return '<div class="card" style="margin-bottom:8px" id="blend-row-' + id + '"><div class="card-body" style="padding:12px 14px">' +
    '<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">' +
    '<input type="radio" name="blend-anchor" id="blend-anchor-' + id + '" ' + checked + ' onchange="setBlendAnchor(' + id + ')" style="width:20px;height:20px">' +
    '<input type="text" id="blend-name-' + id + '" placeholder="Compound name" oninput="updateBlendDoseLabel();runBlendCalc()" style="flex:1;background:var(--bg);border:1px solid var(--border2);border-radius:8px;padding:10px 12px;color:var(--text);font-family:var(--sans);font-size:14px">' +
    '<button onclick="removeBlendRow(' + id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:36px;height:36px;font-size:14px;cursor:pointer;flex-shrink:0">\\u2715</button>' +
    '</div>' +
    '<div class="field"><label>Amount in vial</label><input type="number" id="blend-amount-' + id + '" step="0.01" inputmode="decimal" placeholder="5" oninput="runBlendCalc()"></div>' +
    '<div id="blend-result-' + id + '" style="font-family:var(--mono);font-size:13px;color:var(--muted);margin-top:6px"></div>' +
    '</div></div>';
}

function addBlendRow() {
  const id = BLEND_NEXT_ID++;
  BLEND_ROW_IDS.push(id);
  const container = document.getElementById('blend-rows');
  if (container) container.insertAdjacentHTML('beforeend', renderBlendRowHtml(id));
}

function removeBlendRow(id) {
  if (BLEND_ROW_IDS.length <= 1) return;
  BLEND_ROW_IDS = BLEND_ROW_IDS.filter(function(x) { return x !== id; });
  const row = document.getElementById('blend-row-' + id);
  if (row) row.remove();
  if (BLEND_ANCHOR_ID === id) {
    BLEND_ANCHOR_ID = BLEND_ROW_IDS[0];
    const radio = document.getElementById('blend-anchor-' + BLEND_ANCHOR_ID);
    if (radio) radio.checked = true;
    updateBlendDoseLabel();
  }
  runBlendCalc();
}

function setBlendAnchor(id) {
  BLEND_ANCHOR_ID = id;
  updateBlendDoseLabel();
  runBlendCalc();
}

function updateBlendDoseLabel() {
  const nameInput = document.getElementById('blend-name-' + BLEND_ANCHOR_ID);
  const label = document.getElementById('blend-dose-label');
  const name = (nameInput && nameInput.value.trim()) ? nameInput.value.trim() : 'anchor compound';
  if (label) label.textContent = 'Desired dose of ' + name;
}

function syncBlendUnits(changed) {
  const vialSel = document.getElementById('blend-vial-unit');
  const doseSel = document.getElementById('blend-dose-unit');
  if (!vialSel || !doseSel) return;
  if (changed === 'vial' && vialSel.value === 'IU') doseSel.value = 'IU';
  if (changed === 'dose' && doseSel.value === 'IU') vialSel.value = 'IU';
}

function runBlendCalc() {
  // math built in next step
}

function saveBlendCalcAs() {
  // built in next step
}

function switchCalcTab(name, btn) {'''

n2 = c.count(anchor2)
print("function insert count:", n2)
assert n2 == 1, "aborting"
c = c.replace(anchor2, functions, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
