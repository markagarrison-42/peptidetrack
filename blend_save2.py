c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  const panel = document.getElementById('calc-' + name);
  if (panel) panel.classList.add('active');
}

function syncCalcUnits(changed) {'''
new = '''  const panel = document.getElementById('calc-' + name);
  if (panel) panel.classList.add('active');
  if (name === 'blend') loadSavedBlends();
}

function syncCalcUnits(changed) {'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
