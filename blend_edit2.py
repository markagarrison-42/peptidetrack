c = open('/home/madfella/peptidetrack/static/app.js').read()

old1 = '''let BLEND_ROW_IDS = [];
let BLEND_NEXT_ID = 1;
let BLEND_LAST_EDITED_ID = null;'''
new1 = '''let BLEND_ROW_IDS = [];
let BLEND_NEXT_ID = 1;
let BLEND_LAST_EDITED_ID = null;
let BLEND_EDITING_ID = null;'''
n1 = c.count(old1)
print("global count:", n1)
assert n1 == 1
c = c.replace(old1, new1, 1)

old2 = '''async function deleteSavedBlend(blendId) {'''
new2 = '''async function loadSavedBlend(blendId) {
  try {
    const blends = await GET('/api/saved-calcs/blends');
    const blend = blends.find(function(b) { return b.id === blendId; });
    if (!blend) return;

    BLEND_EDITING_ID = blendId;
    BLEND_ROW_IDS = blend.compounds.map(function(_, i) { return i + 1; });
    BLEND_NEXT_ID = BLEND_ROW_IDS.length + 1;
    BLEND_LAST_EDITED_ID = BLEND_ROW_IDS[0];

    const vialContainer = document.getElementById('blend-vial-rows');
    if (vialContainer) {
      vialContainer.innerHTML = BLEND_ROW_IDS.map(function(id, idx) { return renderBlendVialRowHtml(id, idx); }).join('');
    }
    BLEND_ROW_IDS.forEach(function(id, idx) {
      const nameEl = document.getElementById('blend-name-' + id);
      const amountEl = document.getElementById('blend-amount-' + id);
      if (nameEl) nameEl.value = blend.compounds[idx].name;
      if (amountEl) amountEl.value = blend.compounds[idx].amount;
    });

    const waterEl = document.getElementById('blend-water');
    const vialUnitEl = document.getElementById('blend-vial-unit');
    const doseUnitEl = document.getElementById('blend-dose-unit');
    if (waterEl) waterEl.value = blend.water;
    if (vialUnitEl) vialUnitEl.value = blend.vial_unit;
    if (doseUnitEl) doseUnitEl.value = blend.dose_unit;

    renderBlendDoseRows();
    const resultBox = document.getElementById('blend-result');
    if (resultBox) resultBox.style.display = 'none';

    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) { alert(err.message); }
}

async function deleteSavedBlend(blendId) {'''
n2 = c.count(old2)
print("function count:", n2)
assert n2 == 1
c = c.replace(old2, new2, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
