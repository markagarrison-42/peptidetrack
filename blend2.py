c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''    '<div id="saved-calcs-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">Loading...</div></div>' +
    '</div>';
  loadSavedCalcs();
}

function syncCalcUnits(changed) {'''
new = '''    '<div id="saved-calcs-list"><div style="font-size:12px;color:var(--muted);padding:8px 0">Loading...</div></div>' +
    '</div>' +
    '</div>' +
    '<div class="inner-panel" id="calc-blend">' +
    '<div class="section" style="padding:20px"><div style="font-size:13px;color:var(--muted)">Blend calculator coming up</div></div>' +
    '</div>';
  loadSavedCalcs();
}

function switchCalcTab(name, btn) {
  document.querySelectorAll('#page-calc .inner-tab').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('#page-calc .inner-panel').forEach(function(p) { p.classList.remove('active'); });
  btn.classList.add('active');
  const panel = document.getElementById('calc-' + name);
  if (panel) panel.classList.add('active');
}

function syncCalcUnits(changed) {'''
n = c.count(old)
print("count:", n)
if n == 1:
    c = c.replace(old, new, 1)
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
    print("written")
else:
    print("ABORTED")
