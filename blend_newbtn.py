c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''function renderBlendPanel() {
  BLEND_ROW_IDS = [1, 2];
  BLEND_NEXT_ID = 3;
  BLEND_LAST_EDITED_ID = 1;
  let html = '<div class="section" style="padding:20px">';
  html += '<div class="section-label">Vial details</div>';'''
new = '''function renderBlendPanel() {
  BLEND_ROW_IDS = [1, 2];
  BLEND_NEXT_ID = 3;
  BLEND_LAST_EDITED_ID = 1;
  BLEND_EDITING_ID = null;
  BLEND_LOADED = null;
  let html = '<div class="section" style="padding:20px">';
  html += '<button onclick="startNewBlend()" style="width:100%;margin-bottom:16px;padding:10px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:13px;font-weight:600;cursor:pointer">+ New Blend</button>';
  html += '<div class="section-label">Vial details</div>';'''
n1 = c.count(old)
print("panel count:", n1)
assert n1 == 1
c = c.replace(old, new, 1)

anchor = "function switchCalcTab(name, btn) {"
new_fn = '''function startNewBlend() {
  const panel = document.getElementById('calc-blend');
  if (panel) panel.innerHTML = renderBlendPanel();
}

function switchCalcTab(name, btn) {'''
n2 = c.count(anchor)
print("switchtab count:", n2)
assert n2 == 1
c = c.replace(anchor, new_fn, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
