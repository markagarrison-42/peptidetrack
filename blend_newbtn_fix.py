c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''function startNewBlend() {
  const panel = document.getElementById('calc-blend');
  if (panel) panel.innerHTML = renderBlendPanel();
}'''
new = '''function startNewBlend() {
  const panel = document.getElementById('calc-blend');
  if (panel) panel.innerHTML = renderBlendPanel();
  loadSavedBlends();
}'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
