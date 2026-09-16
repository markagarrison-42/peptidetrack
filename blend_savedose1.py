c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  const compounds = BLEND_ROW_IDS.map(function(id) {
    const nameEl = document.getElementById('blend-name-' + id);
    const amountEl = document.getElementById('blend-amount-' + id);
    return {
      name: nameEl && nameEl.value.trim() ? nameEl.value.trim() : ('Compound ' + id),
      amount: amountEl ? parseFloat(amountEl.value) : null,
    };
  }).filter(function(c) { return c.amount && c.amount > 0; });'''
new = '''  const compounds = BLEND_ROW_IDS.map(function(id) {
    const nameEl = document.getElementById('blend-name-' + id);
    const amountEl = document.getElementById('blend-amount-' + id);
    const result = {
      name: nameEl && nameEl.value.trim() ? nameEl.value.trim() : ('Compound ' + id),
      amount: amountEl ? parseFloat(amountEl.value) : null,
    };
    if (id === BLEND_LAST_EDITED_ID) {
      const doseEl = document.getElementById('blend-desired-' + id);
      const doseVal = doseEl ? parseFloat(doseEl.value) : NaN;
      if (doseVal && doseVal > 0) result.desired_dose = doseVal;
    }
    return result;
  }).filter(function(c) { return c.amount && c.amount > 0; });'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
