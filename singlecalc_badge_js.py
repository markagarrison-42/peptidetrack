c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  document.getElementById('calc-doses').textContent = dosesInVial;
  res.style.display = 'block';
}'''
new = '''  document.getElementById('calc-doses').textContent = dosesInVial;

  const badge = document.getElementById('calc-loaded-badge');
  if (badge) {
    const matches = CALC_LOADED && CALC_LOADED.vial === vial && CALC_LOADED.water === water && CALC_LOADED.dose === dose && CALC_LOADED.vialUnit === vialUnit && CALC_LOADED.doseUnit === doseUnit;
    if (matches) {
      badge.textContent = CALC_LOADED.name;
      badge.style.display = 'inline-block';
    } else {
      badge.style.display = 'none';
    }
  }

  res.style.display = 'block';
}'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
