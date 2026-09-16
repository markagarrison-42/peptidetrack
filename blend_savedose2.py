c = open('/home/madfella/peptidetrack/static/app.js').read()

old = '''    BLEND_ROW_IDS = blend.compounds.map(function(_, i) { return i + 1; });
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
  } catch (err) { alert(err.message); }'''

new = '''    BLEND_ROW_IDS = blend.compounds.map(function(_, i) { return i + 1; });
    BLEND_NEXT_ID = BLEND_ROW_IDS.length + 1;

    const anchorIdx = blend.compounds.findIndex(function(c) { return c.desired_dose; });
    BLEND_LAST_EDITED_ID = anchorIdx >= 0 ? BLEND_ROW_IDS[anchorIdx] : BLEND_ROW_IDS[0];

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

    if (anchorIdx >= 0) {
      const doseEl = document.getElementById('blend-desired-' + BLEND_ROW_IDS[anchorIdx]);
      if (doseEl) doseEl.value = blend.compounds[anchorIdx].desired_dose;
      runBlendCalc();
    } else {
      const resultBox = document.getElementById('blend-result');
      if (resultBox) resultBox.style.display = 'none';
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) { alert(err.message); }'''

n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
