c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  document.getElementById('blend-doses-total').textContent = isFinite(minDoses) ? minDoses.toFixed(2) : '\\u2014';
  if (resultBox) resultBox.style.display = 'block';
}'''
new = '''  document.getElementById('blend-doses-total').textContent = isFinite(minDoses) ? minDoses.toFixed(2) : '\\u2014';

  const badge = document.getElementById('blend-loaded-badge');
  if (badge) {
    let matches = false;
    if (BLEND_LOADED && BLEND_LOADED.water === water && BLEND_LOADED.vialUnit === vialUnit && BLEND_LOADED.doseUnit === doseUnit && BLEND_LOADED.compounds.length === BLEND_ROW_IDS.length) {
      matches = BLEND_ROW_IDS.every(function(id, idx) {
        const nameEl = document.getElementById('blend-name-' + id);
        const amountEl = document.getElementById('blend-amount-' + id);
        const currentName = nameEl ? nameEl.value.trim() : '';
        const currentAmount = amountEl ? parseFloat(amountEl.value) : null;
        return BLEND_LOADED.compounds[idx].name === currentName && BLEND_LOADED.compounds[idx].amount === currentAmount;
      });
    }
    if (matches) {
      badge.textContent = BLEND_LOADED.name;
      badge.style.display = 'inline-block';
    } else {
      badge.style.display = 'none';
    }
  }

  if (resultBox) resultBox.style.display = 'block';
}'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
