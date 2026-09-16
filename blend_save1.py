c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''function saveBlendCalcAs() {
  // built in next step
}

function switchCalcTab(name, btn) {'''
new = '''async function saveBlendCalcAs() {
  const water = parseFloat(document.getElementById('blend-water').value);
  const vialUnit = document.getElementById('blend-vial-unit') ? document.getElementById('blend-vial-unit').value : 'mg';
  const doseUnit = document.getElementById('blend-dose-unit') ? document.getElementById('blend-dose-unit').value : 'mg';
  if (!water || water <= 0) { alert('Enter water amount first'); return; }

  const compounds = BLEND_ROW_IDS.map(function(id) {
    const nameEl = document.getElementById('blend-name-' + id);
    const amountEl = document.getElementById('blend-amount-' + id);
    return {
      name: nameEl && nameEl.value.trim() ? nameEl.value.trim() : ('Compound ' + id),
      amount: amountEl ? parseFloat(amountEl.value) : null,
    };
  }).filter(function(c) { return c.amount && c.amount > 0; });

  if (!compounds.length) { alert('Enter at least one compound amount first'); return; }

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
  } catch (err) { alert(err.message); }
}

async function loadSavedBlends() {
  const el = document.getElementById('saved-blends-list');
  if (!el) return;
  try {
    const blends = await GET('/api/saved-calcs/blends');
    if (!blends.length) {
      el.innerHTML = '<div style="font-size:12px;color:var(--muted);padding:8px 0">No saved blends yet.</div>';
      return;
    }
    let html = '';
    blends.forEach(function(blend) {
      const names = blend.compounds.map(function(c) { return c.name; }).join(' + ');
      html += '<div class="card" style="margin-bottom:8px"><div class="card-body" style="padding:12px 14px;display:flex;justify-content:space-between;align-items:center">';
      html += '<div style="flex:1">';
      html += '<div style="font-size:14px;font-weight:600">' + blend.name + '</div>';
      html += '<div style="font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:2px">' + names + '</div>';
      html += '</div>';
      html += '<button onclick="deleteSavedBlend(' + blend.id + ')" style="background:transparent;border:1px solid var(--border2);border-radius:6px;color:var(--red);width:28px;height:28px;font-size:14px;cursor:pointer;flex-shrink:0;margin-left:8px">\\u2715</button>';
      html += '</div></div>';
    });
    el.innerHTML = html;
  } catch (err) {
    el.innerHTML = '<div style="font-size:12px;color:var(--red);padding:8px 0">' + err.message + '</div>';
  }
}

async function deleteSavedBlend(blendId) {
  if (!confirm('Delete this saved blend?')) return;
  try {
    await DEL('/api/saved-calcs/blends/' + blendId);
    loadSavedBlends();
  } catch (err) { alert(err.message); }
}

function switchCalcTab(name, btn) {'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
