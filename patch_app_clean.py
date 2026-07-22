content = open('/home/madfella/peptidetrack/static/app.js').read()

# 1. Filter out "As needed" from Today tab
# Find the items forEach block and add the filter
old = """      if (!item.active) return;
      const nonSpecific = ['Daily','Weekly','Twice daily','3x/week','Monthly','As needed'];
      if (item.frequency && !nonSpecific.includes(item.frequency)) {
        const days = item.frequency.split(',').map(function(d) { return d.trim(); });
        if (days.length && /^[A-Z][a-z]{2}/.test(days[0]) && !days.includes(todayDay)) return;
      }
      allItems.push({ item: item, protoName: proto.name });"""

new = """      if (!item.active) return;
      if (item.frequency === 'As needed') return;
      const nonSpecific = ['Daily','Weekly','Twice daily','3x/week','Monthly'];
      if (item.frequency && !nonSpecific.includes(item.frequency)) {
        const days = item.frequency.split(',').map(function(d) { return d.trim(); });
        if (days.length && /^[A-Z][a-z]{2}/.test(days[0]) && !days.includes(todayDay)) return;
      }
      allItems.push({ item: item, protoName: proto.name });"""

if old in content:
    content = content.replace(old, new)
    print('As needed filter: OK')
else:
    # Try var version
    old2 = old.replace('const nonSpecific', 'var nonSpecific')
    if old2 in content:
        content = content.replace(old2, new.replace('const nonSpecific', 'var nonSpecific'))
        print('As needed filter (var): OK')
    else:
        print('As needed filter: NOT FOUND')
        idx = content.find('nonSpecific')
        print(repr(content[idx-100:idx+300]))

# 2. Add Tomorrow section
old_tomorrow_anchor = """  el.innerHTML = html;
}

function renderDoseCard("""

new_tomorrow = """  // Tomorrow's schedule
  var tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  var tomorrowDay = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][tomorrow.getDay()];
  var tomorrowItems = [];
  var nonSpecTomorrow = ['Daily','Weekly','Twice daily','3x/week','Monthly'];
  protocols.forEach(function(proto) {
    if (!proto.items) return;
    proto.items.forEach(function(item) {
      if (!item.active) return;
      if (item.frequency === 'As needed') return;
      if (item.frequency && !nonSpecTomorrow.includes(item.frequency)) {
        var tDays = item.frequency.split(',').map(function(d) { return d.trim(); });
        if (!tDays.includes(tomorrowDay)) return;
      }
      tomorrowItems.push(item);
    });
  });
  if (tomorrowItems.length) {
    html += '<div class="tomorrow-section">';
    html += '<div class="tomorrow-label">Tomorrow</div>';
    tomorrowItems.forEach(function(item) {
      var doseUnit = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
      html += '<div class="tomorrow-item">';
      html += '<div class="tomorrow-item-name">' + item.compound_name + '</div>';
      html += '<div class="tomorrow-item-detail">' + item.dose_mg + ' ' + doseUnit;
      if (item.route)         html += ' · ' + item.route;
      if (item.reminder_time) html += ' · 🔔 ' + item.reminder_time;
      html += '</div></div>';
    });
    html += '</div>';
  }

  el.innerHTML = html;
}

function renderDoseCard("""

if old_tomorrow_anchor in content:
    content = content.replace(old_tomorrow_anchor, new_tomorrow, 1)
    print('Tomorrow section: OK')
else:
    print('Tomorrow anchor: NOT FOUND')

# 3. Add "+ Add" button to history date groups
old_date = """    html += '<div class="history-date-group">';
    html += '<div class="history-date-label">' + dateStr + '</div>';"""

new_date = """    html += '<div class="history-date-group">';
    html += '<div class="history-date-label-row">';
    html += '<div class="history-date-label">' + dateStr + '</div>';
    html += '<button class="history-add-btn" data-date="' + d + '" onclick="showAddPastDoseModal(this.getAttribute(\'data-date\'))">+ Add</button>';
    html += '</div>';"""

if old_date in content:
    content = content.replace(old_date, new_date)
    print('History add button: OK')
else:
    print('History date group: NOT FOUND')

# 4. Add showAddPastDoseModal and helpers
old_load_hist = "async function loadHistory(offset) {"
new_past_fn = """function showAddPastDoseModal(dateStr) {
  var modal = document.getElementById('add-past-dose-modal');
  if (!modal) return;
  document.getElementById('apd-date').value = dateStr;
  document.getElementById('apd-date-label').textContent = new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  document.getElementById('apd-dose').value = '';
  document.getElementById('apd-flash').textContent = '';
  var select = document.getElementById('apd-compound');
  select.innerHTML = '';
  var firstDose = '';
  var firstUnit = 'mg';
  (S.protocols || []).filter(function(p) { return p.active; }).forEach(function(proto) {
    (proto.items || []).filter(function(i) { return i.active; }).forEach(function(item) {
      var unit = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
      var opt = document.createElement('option');
      opt.value = item.id + '|' + item.dose_mg + '|' + unit;
      opt.textContent = item.compound_name + ' (' + item.dose_mg + ' ' + unit + ')';
      select.appendChild(opt);
      if (!firstDose) { firstDose = item.dose_mg; firstUnit = unit; }
    });
  });
  document.getElementById('apd-dose').value = firstDose || '';
  document.getElementById('apd-unit').textContent = firstUnit;
  modal.classList.add('open');
}

function closeAddPastDoseModal() {
  var modal = document.getElementById('add-past-dose-modal');
  if (modal) modal.classList.remove('open');
}

function onApdCompoundChange() {
  var select = document.getElementById('apd-compound');
  var parts = select.value.split('|');
  document.getElementById('apd-dose').value = parts[1] || '';
  document.getElementById('apd-unit').textContent = parts[2] || 'mg';
}

async function saveAddPastDose() {
  var dateStr = document.getElementById('apd-date').value;
  var selVal  = document.getElementById('apd-compound').value;
  var parts   = selVal.split('|');
  var itemId  = parseInt(parts[0]);
  var dose    = parseFloat(document.getElementById('apd-dose').value);
  if (isNaN(dose) || dose <= 0) { flash('apd-flash', 'Enter a valid dose', true); return; }
  try {
    await POST('/api/doses/log-past', { protocol_item_id: itemId, dose_mg_taken: dose, local_date: dateStr });
    closeAddPastDoseModal();
    loadHistory(HISTORY_OFFSET);
  } catch (err) { flash('apd-flash', err.message, true); }
}

async function loadHistory(offset) {"""

if old_load_hist in content:
    content = content.replace(old_load_hist, new_past_fn)
    print('Past dose modal fns: OK')
else:
    print('loadHistory: NOT FOUND')

# 5. Add backdrop close for add-past-dose-modal
old_boot_end = """});"""
new_boot_end = """  var apdModal = document.getElementById('add-past-dose-modal');
  if (apdModal) {
    apdModal.addEventListener('click', function(e) {
      if (e.target === apdModal) closeAddPastDoseModal();
    });
  }
});"""
# Replace the last occurrence
last_idx = content.rfind(old_boot_end)
content = content[:last_idx] + new_boot_end + content[last_idx + len(old_boot_end):]
print('Backdrop listener: OK')

open('/home/madfella/peptidetrack/static/app.js', 'w').write(content)
print('\nDone. Verifying...')
import subprocess
result = subprocess.run(['node', '--check', '/home/madfella/peptidetrack/static/app.js'], capture_output=True, text=True)
if result.returncode == 0:
    print('JS VALID')
else:
    print('JS INVALID:', result.stderr[:200])
