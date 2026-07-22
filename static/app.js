'use strict';
/* ══════════════════════════════════════════
   STATE
══════════════════════════════════════════ */
const S = {
  user:      null,
  userId:    null,
  role:      null,
  protocol:  null,
  protocols: [],
  photos:    {},
};
let COMPARE_PHOTOS = {};
let selectedMood   = null;
let onboardStep    = 1;

/* ══════════════════════════════════════════
   API
══════════════════════════════════════════ */
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin' };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Error ' + res.status);
  return data;
}
const GET  = p      => api('GET',    p);
const POST = (p, b) => api('POST',   p, b);
const PUT  = (p, b) => api('PUT',    p, b);
const DEL  = p      => api('DELETE', p);

/* ══════════════════════════════════════════
   HELPERS
══════════════════════════════════════════ */
function today() {
  return new Date().toISOString().split('T')[0];
}
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function fmtDateShort(iso) {
  if (!iso) return '—';
  return new Date(iso + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
function fmtDay() {
  return new Date().toLocaleDateString('en-US', { weekday: 'long' });
}
function fmtMonthDay() {
  return new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
}
function fmt12hr(hhmm) {
  if (!hhmm) return hhmm;
  var parts = hhmm.split(':');
  var h = parseInt(parts[0]);
  var m = parts[1];
  var ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return h + ':' + m + ' ' + ampm;
}

function fmtNum(n, dec) {
  if (dec === undefined) dec = 1;
  if (n == null) return '—';
  return Number(n).toFixed(dec);
}
function initials(name) {
  if (!name) return '?';
  return name.split(' ').map(function(w) { return w[0]; }).join('').toUpperCase().slice(0, 2);
}
function flash(id, msg, isErr) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = 'flash-msg' + (isErr ? ' error' : '');
  setTimeout(function() { el.textContent = ''; }, 3500);
}

function safetyBanner() {
  return '<div class="safety-banner">⚠️ For Research Use Only ⚠️</div>';
}

/* ══════════════════════════════════════════
   AUTH
══════════════════════════════════════════ */
let authMode = 'login';

function toggleAuthMode() {
  authMode = authMode === 'login' ? 'register' : 'login';
  const isReg = authMode === 'register';
  document.getElementById('auth-heading').textContent    = isReg ? 'Create account' : 'Welcome back';
  document.getElementById('auth-sub').textContent        = isReg ? 'Create a free account to get started.' : 'Sign in to your account';
  document.getElementById('auth-submit-btn').textContent = isReg ? 'Create account' : 'Sign in';
  document.getElementById('auth-toggle-btn').textContent = isReg ? 'Already have an account? Sign in' : 'Have an invite code? Register';
  document.getElementById('auth-email-row').style.display = isReg ? 'block' : 'none';
  document.getElementById('auth-name-row').style.display  = isReg ? 'block' : 'none';
  document.getElementById('auth-error').textContent = '';
}

async function authSubmit() {
  const username = document.getElementById('auth-username').value.trim().toLowerCase();
  const password = document.getElementById('auth-password').value;
  const errEl    = document.getElementById('auth-error');
  errEl.textContent = '';
  if (!username || !password) { errEl.textContent = 'Username and password required.'; return; }
  try {
    let data;
    if (authMode === 'register') {
      const email      = document.getElementById('auth-email').value.trim() || null;
      const first_name = document.getElementById('auth-firstname').value.trim() || null;
      const last_name  = document.getElementById('auth-lastname').value.trim() || null;
      data = await POST('/auth/register', { username, password, email, first_name, last_name });
    } else {
      data = await POST('/auth/login', { username, password });
    }
    S.user = data.username;
    S.role = data.role;
    document.getElementById('auth-screen').classList.add('hidden');
    bootApp();
  } catch (err) {
    errEl.textContent = err.message;
  }
}

async function logout() {
  await POST('/auth/logout').catch(function() {});
  S.user = null; S.userId = null; S.role = null;
  location.reload();
}

async function checkAuth() {
  try {
    const me = await GET('/auth/me');
    S.user   = me.username;
    S.userId = me.id;
    S.role   = me.role;
    document.getElementById('auth-screen').classList.add('hidden');
    bootApp();
  } catch (e) {
    // stay on auth screen
  }
}

function showForgotPw() {
  const s = document.getElementById('forgot-section');
  s.style.display = s.style.display === 'none' ? 'block' : 'none';
}

async function requestReset() {
  const username = document.getElementById('forgot-username').value.trim();
  const msgEl    = document.getElementById('reset-msg');
  try {
    const d = await POST('/auth/reset/request', { username });
    msgEl.style.color = 'var(--green)';
    msgEl.textContent = d.message;
  } catch (err) {
    msgEl.style.color = 'var(--red)';
    msgEl.textContent = err.message;
  }
}

async function confirmReset() {
  const pw  = document.getElementById('reset-new-pw').value;
  const pw2 = document.getElementById('reset-confirm-pw').value;
  const err = document.getElementById('reset-error');
  err.textContent = '';
  if (pw !== pw2)    { err.textContent = 'Passwords do not match.'; return; }
  if (pw.length < 6) { err.textContent = 'Min 6 characters.'; return; }
  const token = new URLSearchParams(window.location.search).get('token');
  try {
    await POST('/auth/reset/confirm', { token, password: pw });
    window.history.replaceState({}, '', '/');
    document.getElementById('reset-screen').style.display = 'none';
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('auth-error').style.color = 'var(--green)';
    document.getElementById('auth-error').textContent  = 'Password reset — sign in below.';
  } catch (err2) {
    err.textContent = err2.message;
  }
}

/* ══════════════════════════════════════════
   BOOT
══════════════════════════════════════════ */
async function bootApp() {
  try {
    const me = await GET('/auth/me');
    S.userId = me.id;
    S.user   = me.username;
    S.role   = me.role;
  } catch (e) { return; }

  const profile = await GET('/api/profile/' + S.userId).catch(function() { return null; });
  const displayName = (profile && (profile.first_name || profile.last_name))
    ? [profile.first_name, profile.last_name].filter(Boolean).join(' ')
    : S.user;
  document.getElementById('topbar-name').textContent = displayName;

  loadPeptideDosageData();
  loadToday();

  if (profile && !profile.onboarding_complete) {
    setTimeout(function() { showOnboarding(profile); }, 400);
  }

  setTimeout(initPushNotifications, 3000);
}

/* ══════════════════════════════════════════
   ROUTING
══════════════════════════════════════════ */
function showPage(name, tabEl) {
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
  const page = document.getElementById('page-' + name);
  if (page) page.classList.add('active');
  if (tabEl) tabEl.classList.add('active');
  const loaders = {
    today:    loadToday,
    protocol: loadProtocol,
    progress: loadProgress,
    profile:  loadProfile,
    calc:     loadCalc,
    learn:    loadLearn,
  };
  if (loaders[name]) loaders[name]();
}

/* ══════════════════════════════════════════
   DOSE LOG MODAL
══════════════════════════════════════════ */
function showDoseModal(itemId, compoundName, defaultDose, doseUnit, isUnscheduled) {
  const modal = document.getElementById('dose-modal');
  const title = document.getElementById('dose-modal-title');
  const input = document.getElementById('dose-modal-amount');
  const btn   = document.getElementById('dose-modal-confirm');

  title.textContent = compoundName;
  input.value       = defaultDose;
  input.placeholder = defaultDose;

  // store context on button
  btn.setAttribute('data-item-id',      itemId);
  btn.setAttribute('data-unit',         doseUnit || 'mg');
  btn.setAttribute('data-unscheduled',  isUnscheduled ? '1' : '0');

  document.getElementById('dose-modal-unit').textContent = doseUnit || 'mg';
  modal.classList.add('open');

  setTimeout(function() { input.focus(); input.select(); }, 100);
}

function closeDoseModal() {
  document.getElementById('dose-modal').classList.remove('open');
  const btn = document.getElementById('dose-modal-confirm');
  if (btn) { btn.disabled = false; btn.textContent = 'Log dose'; }
  const flash = document.getElementById('dose-modal-flash');
  if (flash) flash.textContent = '';
  const notesEl = document.getElementById('dose-modal-notes');
  if (notesEl) notesEl.value = '';
}
async function confirmDoseModal() {
  const btn         = document.getElementById('dose-modal-confirm');
  const itemId      = parseInt(btn.getAttribute('data-item-id'));
  const unit        = btn.getAttribute('data-unit');
  const unscheduled = btn.getAttribute('data-unscheduled') === '1';
  const amount      = parseFloat(document.getElementById('dose-modal-amount').value);
  const notesEl     = document.getElementById('dose-modal-notes');
  const notes       = notesEl ? notesEl.value.trim() || null : null;
  const localDate   = new Date().toLocaleDateString('en-CA');

  if (isNaN(amount) || amount <= 0) {
    flash('dose-modal-flash', 'Enter a valid dose', true);
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Logging...';

  try {
    if (unscheduled) {
      await POST('/api/doses/log-unscheduled', {
        protocol_item_id: itemId,
        dose_mg_taken:    amount,
        local_date:       localDate,
        notes:            notes,
      });
    } else {
      await POST('/api/doses/toggle', {
        protocol_item_id: itemId,
        dose_mg_taken:    amount,
        local_date:       localDate,
        notes:            notes,
      });
    }
    closeDoseModal();
    loadTodayLog();
  } catch (err) {
    flash('dose-modal-flash', err.message, true);
    btn.disabled = false;
    btn.textContent = 'Log dose';
  }
}

/* ══════════════════════════════════════════
   TODAY
══════════════════════════════════════════ */
async function loadToday() {
  const el = document.getElementById('page-today');
  HISTORY_OFFSET = 0;
  el.innerHTML = '<div class="today-tabs">'
    + '<button class="today-tab active" id="today-tab-log" onclick="switchTodayTab(&quot;log&quot;, this)">Today</button>'
    + '<button class="today-tab" id="today-tab-history" onclick="switchTodayTab(&quot;history&quot;, this)">History</button>'
    + '</div>'
    + '<div id="today-log-panel"><div class="empty-state">Loading...</div></div>'
    + '<div id="today-history-panel" style="display:none"></div>';
  loadTodayLog();
}

async function loadTodayLog() {
  try {
    const me        = await GET('/auth/me');
    S.userId        = me.id;
    const protocols = await GET('/api/protocols/patient/' + me.id);
    const todayData = await GET('/api/doses/today?local_date=' + new Date().toLocaleDateString('en-CA'));
    const active    = protocols.filter(function(p) { return p.active; });
    S.protocols     = protocols;
    const logPanel  = document.getElementById('today-log-panel');
    if (logPanel) renderToday(logPanel, active, todayData.taken_item_ids || [], todayData.skipped_item_ids || []);
  } catch (err) {
    const logPanel = document.getElementById('today-log-panel');
    if (logPanel) logPanel.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>' + err.message + '</div>';
  }
}

function switchTodayTab(name, btn) {
  document.querySelectorAll('.today-tab').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  document.getElementById('today-log-panel').style.display     = name === 'log'     ? 'block' : 'none';
  document.getElementById('today-history-panel').style.display = name === 'history' ? 'block' : 'none';
  if (name === 'history') loadHistory(0);
}

function showAddPastDoseModal(dateStr) {
  var modal = document.getElementById('add-past-dose-modal');
  document.getElementById('apd-date').value    = dateStr;
  document.getElementById('apd-date-label').textContent = new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  document.getElementById('apd-dose').value    = '';
  document.getElementById('apd-flash').textContent = '';
  // Populate compound select from active protocols
  var select = document.getElementById('apd-compound');
  select.innerHTML = '';
  var items = [];
  (S.protocols || []).filter(function(p) { return p.active; }).forEach(function(proto) {
    (proto.items || []).filter(function(i) { return i.active; }).forEach(function(item) {
      items.push(item);
    });
  });
  items.forEach(function(item) {
    var unit = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
    var opt = document.createElement('option');
    opt.value = item.id + '|' + item.dose_mg + '|' + unit;
    opt.textContent = item.compound_name + ' (' + item.dose_mg + ' ' + unit + ')';
    select.appendChild(opt);
  });
  // Pre-fill dose from selected compound
  if (items.length) {
    var parts = select.value.split('|');
    document.getElementById('apd-dose').value = parts[1] || '';
    document.getElementById('apd-unit').textContent = parts[2] || 'mg';
  }
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
  var dateStr  = document.getElementById('apd-date').value;
  var selVal   = document.getElementById('apd-compound').value;
  var parts    = selVal.split('|');
  var itemId   = parseInt(parts[0]);
  var dose     = parseFloat(document.getElementById('apd-dose').value);
  if (isNaN(dose) || dose <= 0) { flash('apd-flash', 'Enter a valid dose', true); return; }
  try {
    await POST('/api/doses/log-past', {
      protocol_item_id: itemId,
      dose_mg_taken:    dose,
      local_date:       dateStr,
    });
    closeAddPastDoseModal();
    loadHistory(HISTORY_OFFSET);
  } catch (err) { flash('apd-flash', err.message, true); }
}

function showAddPastDoseModal(dateStr) {
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

async function loadHistory(offset) {
  HISTORY_OFFSET = offset || 0;
  const panel = document.getElementById('today-history-panel');
  if (!panel) return;
  panel.innerHTML = '<div class="empty-state">Loading…</div>';
  try {
    const logs = await GET('/api/doses/history?days_offset=' + HISTORY_OFFSET + '&range=30');
    renderHistory(panel, logs, HISTORY_OFFSET);
  } catch (err) {
    panel.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>' + err.message + '</div>';
  }
}

function renderHistory(panel, logs, offset) {
  const rangeStart = offset + 1;
  const rangeEnd   = offset + 30;
  let html = '<div class="history-nav">';
  html += '<button class="history-nav-btn" onclick="loadHistory(' + (offset + 30) + ')"' + (offset >= 60 ? ' disabled' : '') + '>← Older</button>';
  html += '<span class="history-nav-label">Days ' + rangeStart + '–' + rangeEnd + ' ago</span>';
  html += '<button class="history-nav-btn" onclick="loadHistory(' + Math.max(0, offset - 30) + ')"' + (offset === 0 ? ' disabled' : '') + '>Newer →</button>';
  html += '</div>';

  if (!logs.length) {
    html += '<div class="empty-state"><div class="empty-state-icon">📋</div>No doses logged in this period.</div>';
    panel.innerHTML = html;
    return;
  }

  // Group by date
  const byDate = {};
  logs.forEach(function(log) {
    if (!byDate[log.date]) byDate[log.date] = [];
    byDate[log.date].push(log);
  });

  const dates = Object.keys(byDate).sort().reverse();
  dates.forEach(function(d) {
    const dayLogs = byDate[d];
    const dateStr = new Date(d + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    html += '<div class="history-date-group">';
    html += '<div class="history-date-label-row">';
    html += '<div class="history-date-label">' + dateStr + '</div>';
    html += '<button class="history-add-btn" data-date="' + d + '" onclick="showAddPastDoseModal(this.getAttribute(\'data-date\'))">+ Add</button>';
    html += '</div>';
    dayLogs.forEach(function(log) {
      const unit = log.compound_name ? '' : '';
      html += '<div class="history-entry" data-log-id="' + log.id + '">';
      html += '<div class="history-entry-info">';
      html += '<div class="history-entry-name">' + (log.compound_name || 'Unknown') + '</div>';
      html += '<div class="history-entry-dose">' + (log.dose_mg_taken || '—') + ' mg';
      if (log.off_schedule) html += ' <span class="history-off-badge">off-schedule</span>';
      html += '</div>';
      if (log.notes) html += '<div class="history-entry-notes">' + log.notes + '</div>';
      html += '</div>';
      html += '<div class="history-entry-actions">';
      html += '<button class="icon-btn" data-log-id="' + log.id + '" data-dose="' + (log.dose_mg_taken || 0) + '" data-notes="' + (log.notes || '').replace(/"/g, '&quot;') + '" onclick="showEditLog(this)">✏️</button>';
      html += '<button class="icon-btn danger" onclick="deleteLog(' + log.id + ')">✕</button>';
      html += '</div></div>';
    });
    html += '</div>';
  });

  panel.innerHTML = html;
}

function showEditLog(btn) {
  const logId        = btn.getAttribute('data-log-id');
  const currentDose  = btn.getAttribute('data-dose');
  const currentNotes = btn.getAttribute('data-notes') || '';
  const modal = document.getElementById('edit-log-modal');
  document.getElementById('el-log-id').value      = logId;
  document.getElementById('el-dose').value        = currentDose;
  document.getElementById('el-notes').value       = currentNotes;
  document.getElementById('el-flash').textContent = '';
  modal.classList.add('open');
}

function closeEditLog() {
  const modal = document.getElementById('edit-log-modal');
  if (modal) modal.classList.remove('open');
}

async function saveEditLog() {
  const logId = parseInt(document.getElementById('el-log-id').value);
  const dose  = parseFloat(document.getElementById('el-dose').value);
  const notes = document.getElementById('el-notes').value.trim();
  if (isNaN(dose) || dose <= 0) { flash('el-flash', 'Enter a valid dose', true); return; }
  try {
    await PUT('/api/doses/logs/' + logId, { dose_mg_taken: dose, notes: notes || null });
    closeEditLog();
    loadHistory(HISTORY_OFFSET);
  } catch (err) { flash('el-flash', err.message, true); }
}

async function deleteLog(logId) {
  if (!confirm('Delete this dose log? This cannot be undone.')) return;
  try {
    await DEL('/api/doses/logs/' + logId);
    loadHistory(HISTORY_OFFSET);
  } catch (err) { alert(err.message); }
}

function renderToday(el, protocols, takenIds, skippedIds) {
  const dayName  = fmtDay();
  const dateFull = fmtMonthDay();
  const todayDay = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][new Date().getDay()];

  let html = safetyBanner() + '<div class="date-header">';
  html += '<span class="date-day">' + dayName + '</span>';
  html += '<span class="date-rest">' + dateFull + '</span>';
  html += '</div>';

  if (!protocols.length) {
    html += '<div class="empty-state"><div class="empty-state-icon">💊</div>No active protocol yet.<br>Go to the Protocol tab to create one.</div>';
    el.innerHTML = html;
    return;
  }

  const allItems = [];
  protocols.forEach(function(proto) {
    if (!proto.items) return;
    proto.items.forEach(function(item) {
      if (!item.active) return;
      if (item.frequency === 'As needed') return;
      const nonSpecific = ['Daily','Weekly','Twice daily','3x/week','Monthly'];
      if (item.frequency && !nonSpecific.includes(item.frequency)) {
        const days = item.frequency.split(',').map(function(d) { return d.trim(); });
        if (days.length && /^[A-Z][a-z]{2}/.test(days[0]) && !days.includes(todayDay)) return;
      }
      allItems.push({ item: item, protoName: proto.name });
    });
  });

  if (!allItems.length) {
    html += '<div class="empty-state"><div class="empty-state-icon">✓</div>Nothing scheduled today.<br>Enjoy your rest day!</div>';
    // Still show unscheduled button even on rest days
    html += renderUnscheduledSection(protocols);
    el.innerHTML = html;
    return;
  }

  const taken = allItems.filter(function(e) { return takenIds.includes(e.item.id); }).length;
  const pct   = Math.round(taken / allItems.length * 100);

  html += '<div class="section">';
  html += '<div class="progress-ring-wrap">';
  html += '<div><div class="progress-count">' + taken + '<small>/' + allItems.length + '</small></div><div class="progress-label">logged today</div></div>';
  html += '<div class="progress-track"><div class="progress-fill" style="width:' + pct + '%"></div></div>';
  html += '<div style="font-family:var(--mono);font-size:28px;font-weight:700;color:' + (pct === 100 ? 'var(--green)' : 'var(--muted)') + '">' + pct + '<span style="font-size:14px;color:var(--muted)">%</span></div>';
  html += '</div>';

  const multiProto = protocols.length > 1;
  if (multiProto) {
    protocols.forEach(function(proto) {
      const protoItems = allItems.filter(function(e) { return e.protoName === proto.name; });
      if (!protoItems.length) return;
      html += '<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--accent);margin:16px 0 6px">' + proto.name + '</div>';
      protoItems.forEach(function(e) { html += renderDoseCard(e.item, takenIds, skippedIds); });
    });
  } else {
    allItems.forEach(function(e) { html += renderDoseCard(e.item, takenIds, skippedIds); });
  }

  html += '</div>';

  // Unscheduled section
  html += renderUnscheduledSection(protocols);

  // Tomorrow's schedule
  var tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  var tomorrowDay = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][tomorrow.getDay()];
  var tomorrowItems = [];
  var nonSpecific = ['Daily','Weekly','Twice daily','3x/week','Monthly','As needed'];
  protocols.forEach(function(proto) {
    if (!proto.items) return;
    proto.items.forEach(function(item) {
      if (!item.active) return;
      if (item.frequency && !nonSpecific.includes(item.frequency)) {
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
      if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);
      html += '</div></div>';
    });
    html += '</div>';
  }

  // Tomorrow's schedule
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
      if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);
      html += '</div></div>';
    });
    html += '</div>';
  }

  el.innerHTML = html;
}

function renderDoseCard(item, takenIds, skippedIds) {
  var isTaken   = takenIds.includes(item.id);
  var isSkipped = (skippedIds || []).includes(item.id);
  var doseUnit  = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
  var cardClass = 'dose-card' + (isTaken ? ' taken' : '') + (isSkipped ? ' skipped' : '');
  var symbol    = isTaken ? '✓' : (isSkipped ? '—' : '+');
  var btnClass  = 'dose-check' + (isTaken ? ' checked' : '') + (isSkipped ? ' skipped-check' : '');
  var html = '<div class="' + cardClass + '">';
  html += '<button class="' + btnClass + '"';
  html += ' data-item-id="' + item.id + '"';
  html += ' data-name="' + item.compound_name.replace(/"/g, '&quot;') + '"';
  html += ' data-dose="' + item.dose_mg + '"';
  html += ' data-unit="' + doseUnit + '"';
  html += ' data-taken="' + (isTaken ? '1' : '0') + '"';
  html += ' data-skipped="' + (isSkipped ? '1' : '0') + '"';
  html += ' onclick="handleDoseTap(this)">';
  html += '<span class="dose-check-symbol">' + symbol + '</span>';
  html += '</button>';
  html += '<div class="dose-info">';
  html += '<div class="dose-name">' + item.compound_name + '</div>';
  html += '<div class="dose-meta">' + item.dose_mg + ' ' + doseUnit;
  if (item.frequency) html += ' · ' + item.frequency;
  if (item.route)     html += ' · ' + item.route;
  if (item.timing)    html += ' · ' + item.timing;
  html += '</div>';
  if (item.dose_units) {
    html += '<div class="dose-units-badge">💉 ' + item.dose_units + ' units</div>';
  }
  html += '</div>';
  if (!isTaken && !isSkipped) {
    html += '<button class="skip-btn" data-item-id="' + item.id + '" onclick="handleSkipTap(this)">Skip</button>';
  }
  html += '</div>';
  return html;
}
async function handleDoseTap(btn) {
  var itemId    = parseInt(btn.getAttribute('data-item-id'));
  var name      = btn.getAttribute('data-name');
  var dose      = parseFloat(btn.getAttribute('data-dose'));
  var unit      = btn.getAttribute('data-unit');
  var isTaken   = btn.getAttribute('data-taken') === '1';
  var isSkipped = btn.getAttribute('data-skipped') === '1';
  if (isTaken || isSkipped) {
    try {
      await POST('/api/doses/toggle', { protocol_item_id: itemId, local_date: new Date().toLocaleDateString('en-CA') });
      loadTodayLog();
    } catch (err) { alert(err.message); }
  } else {
    showDoseModal(itemId, name, dose, unit);
  }
}

async function handleSkipTap(btn) {
  var itemId = parseInt(btn.getAttribute('data-item-id'));
  try {
    await POST('/api/doses/skip', { protocol_item_id: itemId, local_date: new Date().toLocaleDateString('en-CA') });
    loadTodayLog();
  } catch (err) { alert(err.message); }
}

function renderUnscheduledSection(protocols) {
  // Gather all active items across all active protocols
  const activeItems = [];
  protocols.filter(function(p) { return p.active; }).forEach(function(proto) {
    if (!proto.items) return;
    proto.items.forEach(function(item) {
      if (!item.active) return;
      activeItems.push({ item: item, protoName: proto.name });
    });
  });

  if (!activeItems.length) return '';

  let html = '<div class="unscheduled-section">';
  html += '<div class="unscheduled-header">';
  html += '<span class="unscheduled-label">Log unscheduled dose</span>';
  html += '<button class="unscheduled-toggle" onclick="toggleUnscheduledPanel(this)">＋</button>';
  html += '</div>';
  html += '<div class="unscheduled-panel" id="unscheduled-panel" style="display:none">';
  html += '<div class="unscheduled-list">';
  activeItems.forEach(function(e) {
    const item     = e.item;
    const doseUnit = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
    html += '<button class="unscheduled-item" onclick="showDoseModal(' + item.id + ', \'' + item.compound_name.replace(/'/g, "\\'") + '\', ' + item.dose_mg + ', \'' + doseUnit + '\', true)">';
    html += '<span class="unscheduled-item-name">' + item.compound_name + '</span>';
    html += '<span class="unscheduled-item-dose">' + item.dose_mg + ' ' + doseUnit + '</span>';
    html += '</button>';
  });
  html += '</div>';
  html += '<div style="font-size:11px;color:var(--muted);padding:8px 16px 12px;font-style:italic">Off-schedule doses won\'t count toward today\'s progress.</div>';
  html += '</div></div>';
  return html;
}

function toggleUnscheduledPanel(btn) {
  const panel = document.getElementById('unscheduled-panel');
  if (!panel) return;
  const open = panel.style.display !== 'none';
  panel.style.display = open ? 'none' : 'block';
  btn.textContent = open ? '＋' : '－';
}

function refreshProgress() {
  const cards = document.querySelectorAll('.dose-card');
  const taken = document.querySelectorAll('.dose-card.taken').length;
  const total = cards.length;
  const pct   = total ? Math.round(taken / total * 100) : 0;
  const fill  = document.querySelector('.progress-fill');
  const count = document.querySelector('.progress-count');
  const pctEl = document.querySelector('.progress-ring-wrap > div:last-child');
  if (fill)  fill.style.width = pct + '%';
  if (count) count.innerHTML  = taken + '<small>/' + total + '</small>';
  if (pctEl) {
    pctEl.innerHTML    = pct + '<span style="font-size:14px;color:var(--muted)">%</span>';
    pctEl.style.color  = pct === 100 ? 'var(--green)' : 'var(--muted)';
  }
}

/* ══════════════════════════════════════════
   PROTOCOL
══════════════════════════════════════════ */
async function loadProtocol() {
  const el = document.getElementById('page-protocol');
  el.innerHTML = '<div style="padding:20px;color:var(--muted);font-size:13px">Loading...</div>';
  try {
    const me        = await GET('/auth/me');
    S.userId        = me.id;
    const protocols = await GET('/api/protocols/patient/' + me.id);
    S.protocols     = protocols;
    renderProtocol(el, protocols, me.id);
  } catch (err) {
    el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>' + err.message + '</div>';
  }
}

function renderProtocol(el, protocols, patientId) {
  let html = safetyBanner();
  const active   = protocols.filter(function(p) { return p.active; });
  const inactive = protocols.filter(function(p) { return !p.active; });

  if (!protocols.length) {
    html += '<div class="empty-state" style="padding:32px 0 20px"><div class="empty-state-icon">📋</div>No protocols yet.<br>Create one below to start tracking.</div>';
  } else {
    if (active.length) {
      html += '<div style="padding:20px 20px 4px"><div class="section-label">Active</div></div>';
      active.forEach(function(proto) { html += renderProtocolCard(proto, patientId); });
    }
    if (inactive.length) {
      html += '<div style="padding:12px 20px 4px"><div class="section-label">Paused</div></div>';
      inactive.forEach(function(proto) { html += renderProtocolCard(proto, patientId); });
    }
  }

  html += '<div style="padding:12px 20px 4px"><div class="section-label">New protocol</div></div>';
  html += '<div style="padding:0 20px 20px">';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Protocol name</label><input type="text" id="new-proto-name" placeholder="e.g. Body Recomp, Sleep Stack, TRT"></div>';
  html += '<div class="field"><label>Start date</label><input type="date" id="new-proto-start" value="' + today() + '"></div>';
  html += '<button class="btn btn-primary" onclick="createMyProtocol(' + patientId + ')">Create protocol</button>';
  html += '<div id="proto-flash" class="flash-msg"></div>';
  html += '</div></div></div>';

  el.innerHTML = html;
}

function renderProtocolCard(proto, patientId) {
  const items    = proto.items ? proto.items.filter(function(i) { return i.active; }) : [];
  const weeksOn  = proto.start_date ? Math.floor((new Date() - new Date(proto.start_date + 'T00:00:00')) / (7 * 24 * 60 * 60 * 1000)) : null;
  const isActive = proto.active;

  let html = '<div style="padding:0 20px 10px">';
  html += '<div class="card"><div class="card-body">';

  html += '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:12px">';
  html += '<div style="flex:1">';
  html += '<div style="font-size:17px;font-weight:700;letter-spacing:-0.3px">' + proto.name + '</div>';
  if (proto.start_date) {
    html += '<div style="font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:3px">Started ' + fmtDateShort(proto.start_date) + (weeksOn !== null ? ' &nbsp;·&nbsp; Week ' + weeksOn : '') + '</div>';
  }
  html += '</div>';
  html += '<div style="display:flex;gap:6px;align-items:center">';
  html += '<button onclick="toggleProtocolActive(' + proto.id + ', ' + patientId + ')" style="padding:5px 12px;border-radius:6px;border:1px solid var(--border2);background:' + (isActive ? 'var(--accent)' : 'transparent') + ';color:' + (isActive ? '#080f1a' : 'var(--muted)') + ';font-family:var(--mono);font-size:11px;font-weight:700;cursor:pointer">' + (isActive ? 'ACTIVE' : 'PAUSED') + '</button>';
  html += '<button onclick="editProtocolName(' + proto.id + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--sans);font-size:12px;cursor:pointer">Edit</button>';
  html += '</div></div>';

  if (!items.length) {
    html += '<div style="font-size:13px;color:var(--muted);margin-bottom:12px">No compounds yet — add one below.</div>';
  } else {
    items.forEach(function(item) {
      const itemUnit = (item.notes && item.notes.startsWith('unit:')) ? item.notes.split(':')[1] : 'mg';
      const sUnit    = itemUnit;
      // Compound wrapper - includes info row + syringe guide, separated from next compound
      html += '<div style="padding:16px 0;border-bottom:3px solid var(--border2)">';
      // Info row
      html += '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:8px">';
      html += '<div style="flex:1">';
      html += '<div style="font-size:15px;font-weight:600">' + item.compound_name + '</div>';
      html += '<div style="font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:3px">';
      html += item.dose_mg + ' ' + itemUnit;
      if (item.frequency)     html += ' · ' + item.frequency;
      if (item.route)         html += ' · ' + item.route;
      if (item.timing)        html += ' · ' + item.timing;
      if (item.reminder_time) html += ' · 🔔 ' + fmt12hr(item.reminder_time);
      html += '</div>';
      if (item.dose_units) {
        html += '<div style="font-family:var(--mono);font-size:11px;color:var(--accent);background:rgba(0,229,212,0.08);padding:2px 8px;border-radius:4px;margin-top:5px;display:inline-block">💉 ' + item.dose_units + ' units</div>';
      }
      html += '</div>';
      html += '<div style="display:flex;gap:6px;flex-shrink:0">';
      html += '<button onclick="editCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-size:12px;cursor:pointer">Edit</button>';
      html += '<button onclick="removeCompoundItem(' + item.id + ', ' + patientId + ')" style="padding:5px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--red);font-size:12px;cursor:pointer">✕</button>';
      html += '</div></div>';
      // Syringe guide (same compound block)
      if (item.dose_units && item.vial_size_mg) {
        html += '<div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 12px">';
        html += '<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Syringe guide</div>';
        html += '<div style="font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.9">';
        html += item.vial_size_mg + sUnit + ' vial / ' + item.recon_volume_ml + 'mL bac water = ' + item.concentration_mg_per_ml + ' ' + sUnit + '/mL<br>';
        html += item.dose_mg + sUnit + ' dose = ' + item.dose_ml + ' mL';
        html += '</div>';
        html += '<div style="margin-top:8px"><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:4px">Draw to this line</div>';
        html += '<div style="font-family:var(--mono);font-size:32px;font-weight:700;color:var(--accent);line-height:1">' + item.dose_units + '<span style="font-size:14px;color:var(--muted)"> units</span></div></div>';
        html += '</div>';
      }
      html += '</div>'; // end compound wrapper
    });
  }

  if (isActive) {
    html += '<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border)">';
    html += '<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:10px">Add compound</div>';
    html += renderAddCompoundForm(proto.id);
    html += '</div>';
  }

  html += '</div></div></div>';
  return html;
}

async function toggleProtocolActive(protocolId, patientId) {
  try {
    const proto = (S.protocols || []).find(function(p) { return p.id === protocolId; });
    if (!proto) return;
    await PUT('/api/protocols/' + protocolId, { active: !proto.active });
    loadProtocol();
    if (document.getElementById('page-today').classList.contains('active')) loadToday();
  } catch (err) { alert(err.message); }
}

function renderAddCompoundForm(protocolId) {
  let html = '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Name</label><input type="text" id="ac-name-' + protocolId + '" placeholder="e.g. Semaglutide, Vitamin D, TRT"></div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Dose</label><input type="number" id="ac-dose-' + protocolId + '" step="0.01" inputmode="decimal" placeholder="0.5"></div>';
  html += '<div class="field"><label>Unit</label><select id="ac-unit-' + protocolId + '" onchange="updateVialLabel(' + protocolId + ')"><option>mg</option><option>mcg</option><option>IU</option><option>mL</option><option>g</option></select></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Frequency</label><select id="ac-freq-' + protocolId + '" onchange="toggleDayPicker(this.value, \'ac-days-' + protocolId + '\')"><option>Daily</option><option>Weekly</option><option>Twice daily</option><option>3x/week</option><option>Monthly</option><option>As needed</option><option>Specific days</option></select></div>';
  html += '<div class="field"><label>Route</label><select id="ac-route-' + protocolId + '" onchange="toggleReconSection(this.value, ' + protocolId + ')"><option>SubQ</option><option>IM</option><option>Oral</option><option>Sublingual</option><option>Intranasal</option><option>Topical</option><option>Patch</option><option>IV</option></select></div>';
  html += '</div>';
  html += '<div class="field"><label>Timing (optional)</label><input type="text" id="ac-timing-' + protocolId + '" placeholder="e.g. Fasted AM, With food, Pre-bed"></div>';
  html += '<div class="field"><label>Reminder time (optional)</label><input type="time" id="ac-reminder-' + protocolId + '"></div>';
  html += '<div class="field" id="ac-days-' + protocolId + '" style="display:none"><label>Specific days</label>';
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">';
  ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach(function(d) {
    html += '<button type="button" id="ac-day-' + protocolId + '-' + d + '" data-day="' + d + '" onclick="toggleDayBtn(this)" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-family:var(--mono);font-size:12px;cursor:pointer;transition:all 0.15s;min-width:44px">' + d + '</button>';
  });
  html += '</div></div>';
  html += '<div id="ac-recon-' + protocolId + '">';
  html += '<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin:12px 0 8px">Reconstitution (leave blank if pre-filled)</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label id="ac-vial-label-' + protocolId + '">Vial size (mg)</label><input type="number" id="ac-vial-' + protocolId + '" step="0.1" inputmode="decimal" placeholder="5"></div>';
  html += '<div class="field"><label>Bac water (mL)</label><input type="number" id="ac-water-' + protocolId + '" step="0.1" inputmode="decimal" placeholder="2"></div>';
  html += '</div></div>';
  html += '<button class="btn btn-primary" style="margin-top:4px" onclick="addMyCompound(' + protocolId + ')">Add</button>';
  html += '<div id="ac-flash-' + protocolId + '" class="flash-msg"></div>';
  html += '</div></div>';
  return html;
}

function toggleReconSection(route, protocolId) {
  const sec = document.getElementById('ac-recon-' + protocolId);
  if (!sec) return;
  const injectable = ['SubQ', 'IM', 'IV'].includes(route);
  sec.style.display = injectable ? 'block' : 'none';
}

function updateVialLabel(protocolId) {
  const unit  = document.getElementById('ac-unit-' + protocolId);
  const label = document.getElementById('ac-vial-label-' + protocolId);
  if (unit && label) label.textContent = 'Vial size (' + unit.value + ')';
}


function toggleDayPicker(val, rowId, labelId) {
  var row   = document.getElementById(rowId);
  var label = labelId ? document.getElementById(labelId) : null;
  var showDays = (val === 'Specific days' || val === 'Weekly' || val === '3x/week');
  if (row) row.style.display = showDays ? 'block' : 'none';
  if (label) {
    if (val === 'Weekly')       label.textContent = 'Which day? (pick 1)';
    else if (val === '3x/week') label.textContent = 'Which days? (pick 3)';
    else                        label.textContent = 'Specific days';
  }
}
function toggleDayBtn(btn) {
  const active = btn.getAttribute('data-selected') === 'true';
  if (active) {
    btn.setAttribute('data-selected', 'false');
    btn.style.background  = 'transparent';
    btn.style.color       = 'var(--muted)';
    btn.style.borderColor = 'var(--border2)';
  } else {
    btn.setAttribute('data-selected', 'true');
    btn.style.background  = 'var(--accent)';
    btn.style.color       = '#080f1a';
    btn.style.borderColor = 'var(--accent)';
  }
}

function getSelectedDays(protocolId) {
  const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  return days.filter(function(d) {
    const el = document.getElementById('ac-day-' + protocolId + '-' + d);
    return el && el.getAttribute('data-selected') === 'true';
  }).join(', ');
}

async function createMyProtocol(patientId) {
  const name  = document.getElementById('new-proto-name').value.trim();
  const start = document.getElementById('new-proto-start').value;
  if (!name) { flash('proto-flash', 'Enter a protocol name', true); return; }
  try {
    await POST('/api/protocols/', { patient_id: patientId, name, start_date: start });
    loadProtocol();
  } catch (err) { flash('proto-flash', err.message, true); }
}

async function addMyCompound(protocolId) {
  const name = document.getElementById('ac-name-' + protocolId).value.trim();
  const dose = document.getElementById('ac-dose-' + protocolId).value;
  if (!name || !dose) { flash('ac-flash-' + protocolId, 'Name and dose required', true); return; }
  try {
    const route      = document.getElementById('ac-route-' + protocolId).value;
    const freqRaw    = document.getElementById('ac-freq-' + protocolId).value;
    const needsDays  = (freqRaw === 'Specific days' || freqRaw === 'Weekly' || freqRaw === '3x/week');
    const frequency  = needsDays ? (getSelectedDays(protocolId) || freqRaw) : freqRaw;
    const unit       = document.getElementById('ac-unit-' + protocolId).value;
    const injectable = ['SubQ', 'IM', 'IV'].includes(route);
    const compound   = await POST('/api/compounds/', {
      name, category: 'Other',
      default_route: route, frequency: frequency,
    });
    await POST('/api/protocols/' + protocolId + '/items', {
      compound_id:     compound.id,
      dose_mg:         parseFloat(dose),
      frequency:       frequency,
      route:           route,
      timing:          document.getElementById('ac-timing-' + protocolId).value || null,
      vial_size_mg:    (injectable && document.getElementById('ac-vial-' + protocolId).value) ? document.getElementById('ac-vial-' + protocolId).value : null,
      recon_volume_ml: (injectable && document.getElementById('ac-water-' + protocolId).value) ? document.getElementById('ac-water-' + protocolId).value : null,
      notes:           unit !== 'mg' ? 'unit:' + unit : null,
      reminder_time:   document.getElementById('ac-reminder-' + protocolId) ? document.getElementById('ac-reminder-' + protocolId).value || null : null,
    });
    loadProtocol();
  } catch (err) { flash('ac-flash-' + protocolId, err.message, true); }
}

function editCompoundItem(itemId, patientId) {
  let foundItem = null;
  (S.protocols || []).forEach(function(proto) {
    (proto.items || []).forEach(function(item) {
      if (item.id === itemId) foundItem = item;
    });
  });
  if (!foundItem) return;
  const unit = (foundItem.notes && foundItem.notes.startsWith('unit:')) ? foundItem.notes.split(':')[1] : 'mg';
  showEditCompoundModal(itemId, foundItem.compound_name, foundItem.dose_mg, unit, foundItem.frequency, foundItem.route, foundItem.timing, foundItem.vial_size_mg, foundItem.recon_volume_ml, foundItem);
}

function showEditCompoundModal(itemId, name, dose, unit, frequency, route, timing, vialSize, reconVol, foundItem) {
  const modal = document.getElementById('edit-compound-modal');
  document.getElementById('ecm-item-id').value    = itemId;
  document.getElementById('ecm-name').textContent = name;
  document.getElementById('ecm-dose').value       = dose;
  document.getElementById('ecm-unit').textContent = unit;
  document.getElementById('ecm-timing').value     = timing || '';
  const freqSel = document.getElementById('ecm-frequency');
  const isSpecific = frequency && !['Daily','Weekly','Twice daily','3x/week','Monthly','As needed'].includes(frequency);
  if (freqSel) {
    freqSel.value = isSpecific ? 'Specific days' : (frequency || 'Daily');
  }
  // Reset day buttons
  ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach(function(d) {
    const btn = document.getElementById('ecm-day-' + d);
    if (btn) { btn.setAttribute('data-selected', 'false'); btn.classList.remove('day-btn-active'); }
  });
  // Pre-select days if specific days
  if (isSpecific && frequency) {
    frequency.split(',').map(function(d) { return d.trim(); }).forEach(function(d) {
      const btn = document.getElementById('ecm-day-' + d);
      if (btn) { btn.setAttribute('data-selected', 'true'); btn.classList.add('day-btn-active'); }
    });
  }
  toggleEcmDayPicker(isSpecific ? 'Specific days' : (frequency || 'Daily'));
  const routeSel = document.getElementById('ecm-route');
  if (routeSel) {
    routeSel.value = route || 'SubQ';
    routeSel.onchange = function() {
      var ecRecon = document.getElementById('ecm-recon');
      if (ecRecon) ecRecon.style.display = ['SubQ','IM','IV'].includes(this.value) ? 'block' : 'none';
    };
  }
  document.getElementById('ecm-flash').textContent = '';
  // Reconstitution fields
  var ecRecon = document.getElementById('ecm-recon');
  var injectable = ['SubQ','IM','IV'].includes(route || 'SubQ');
  if (ecRecon) ecRecon.style.display = injectable ? 'block' : 'none';
  if (document.getElementById('ecm-vial'))     document.getElementById('ecm-vial').value     = vialSize  || '';
  if (document.getElementById('ecm-water'))    document.getElementById('ecm-water').value    = reconVol  || '';
  if (document.getElementById('ecm-reminder')) document.getElementById('ecm-reminder').value = foundItem ? (foundItem.reminder_time || '') : '';
  modal.classList.add('open');
}

function closeEditCompoundModal() {
  const modal = document.getElementById('edit-compound-modal');
  if (modal) modal.classList.remove('open');
}

function toggleEcmDayPicker(val) {
  const picker = document.getElementById('ecm-days');
  if (picker) picker.style.display = val === 'Specific days' ? 'block' : 'none';
}

function toggleEcmDayBtn(btn) {
  const active = btn.getAttribute('data-selected') === 'true';
  btn.setAttribute('data-selected', active ? 'false' : 'true');
  btn.classList.toggle('day-btn-active', !active);
}

function getEcmSelectedDays() {
  return ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].filter(function(d) {
    const el = document.getElementById('ecm-day-' + d);
    return el && el.getAttribute('data-selected') === 'true';
  }).join(', ');
}

async function saveEditCompoundModal() {
  const itemId  = parseInt(document.getElementById('ecm-item-id').value);
  const dose    = parseFloat(document.getElementById('ecm-dose').value);
  const timing  = document.getElementById('ecm-timing').value.trim();
  const freqRaw = document.getElementById('ecm-frequency').value;
  const freq    = freqRaw === 'Specific days' ? (getEcmSelectedDays() || 'Specific days') : freqRaw;
  const route   = document.getElementById('ecm-route').value;
  if (isNaN(dose) || dose <= 0) { flash('ecm-flash', 'Enter a valid dose', true); return; }
  var vial  = document.getElementById('ecm-vial')  ? parseFloat(document.getElementById('ecm-vial').value)  || null : null;
  var water = document.getElementById('ecm-water') ? parseFloat(document.getElementById('ecm-water').value) || null : null;
  try {
    const reminder = document.getElementById('ecm-reminder') ? document.getElementById('ecm-reminder').value || null : null;
    await PUT('/api/protocols/items/' + itemId, {
      dose_mg:         dose,
      timing:          timing || null,
      frequency:       freq,
      route:           route,
      vial_size_mg:    vial,
      recon_volume_ml: water,
      reminder_time:   reminder,
    });
    closeEditCompoundModal();
    loadProtocol();
  } catch (err) { flash('ecm-flash', err.message, true); }
}

async function removeCompoundItem(itemId, patientId) {
  if (!confirm('Remove this compound from your protocol?')) return;
  try {
    await DEL('/api/protocols/items/' + itemId);
    loadProtocol();
  } catch (err) { alert(err.message); }
}

function editProtocolName(protocolId) {
  const proto = (S.protocols || []).find(function(p) { return p.id === protocolId; });
  if (!proto) return;
  showEditProtocolModal(protocolId, proto.name, proto.start_date);
}

function showEditProtocolModal(protocolId, name, startDate) {
  const modal = document.getElementById('edit-protocol-modal');
  document.getElementById('epm-proto-id').value = protocolId;
  document.getElementById('epm-name').value     = name || '';
  document.getElementById('epm-start').value    = startDate || today();
  document.getElementById('epm-flash').textContent = '';
  modal.classList.add('open');
}

function closeEditProtocolModal() {
  const modal = document.getElementById('edit-protocol-modal');
  if (modal) modal.classList.remove('open');
}

async function saveEditProtocolModal() {
  const protocolId = parseInt(document.getElementById('epm-proto-id').value);
  const name       = document.getElementById('epm-name').value.trim();
  const start      = document.getElementById('epm-start').value;
  if (!name) { flash('epm-flash', 'Enter a protocol name', true); return; }
  try {
    await PUT('/api/protocols/' + protocolId, { name: name, start_date: start });
    closeEditProtocolModal();
    loadProtocol();
  } catch (err) { flash('epm-flash', err.message, true); }
}

/* ══════════════════════════════════════════
   PROGRESS
══════════════════════════════════════════ */
async function loadProgress() {
  const el = document.getElementById('page-progress');
  el.innerHTML = '<div class="empty-state">Loading...</div>';
  try {
    const me = await GET('/auth/me');
    S.userId = me.id;
    const [checkins, photos] = await Promise.all([
      GET('/api/checkins/patient/' + me.id),
      GET('/api/photos/patient/' + me.id),
    ]);
    S.photos = {};
    photos.forEach(function(p) {
      if (!S.photos[p.date]) S.photos[p.date] = [];
      S.photos[p.date].push(p);
    });
    COMPARE_PHOTOS = S.photos;
    renderProgress(el, checkins, photos, me.id);
  } catch (err) {
    el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>' + err.message + '</div>';
  }
}

function renderProgress(el, checkins, photos, patientId) {
  let html = safetyBanner();

  html += '<div class="inner-tabs">';
  html += '<button class="inner-tab active" onclick="switchProgressTab(\'body\', this)">Body</button>';
  html += '</div>';

  html += '<div class="inner-panel active" id="prog-body">';
  html += renderBodyPanel(checkins, patientId);
  html += '</div>';



  el.innerHTML = html;

  const weightData = checkins.filter(function(c) { return c.weight_lbs; }).slice().reverse().slice(-20);
  if (weightData.length > 1) {
    setTimeout(function() {
      const canvas = document.getElementById('weight-chart');
      if (!canvas) return;
      new Chart(canvas, {
        type: 'line',
        data: {
          labels:   weightData.map(function(c) { return fmtDateShort(c.date); }),
          datasets: [{
            data:               weightData.map(function(c) { return c.weight_lbs; }),
            borderColor:        '#00d4c8',
            borderWidth:        2,
            pointRadius:        3,
            pointBackgroundColor: '#00d4c8',
            tension:            0.3,
            fill:               false,
          }],
        },
        options: {
          responsive:          true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#5a8099', font: { size: 10 } } },
            y: { grid: { color: '#1a2d42' }, ticks: { color: '#5a8099', font: { size: 10 } } },
          },
        },
      });
    }, 100);
  }
}

function switchProgressTab(name, btn) {
  document.querySelectorAll('.inner-tab').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('.inner-panel').forEach(function(p) { p.classList.remove('active'); });
  btn.classList.add('active');
  const panel = document.getElementById('prog-' + name);
  if (panel) panel.classList.add('active');
  if (name === 'compare') setTimeout(renderComparison, 50);
}

function renderBodyPanel(checkins, patientId) {
  const last = checkins[0];
  let html = '<div style="padding:20px">';

  if (last) {
    html += '<div class="section-label">Latest measurements</div>';
    html += '<div class="stat-grid">';
    html += '<div class="stat-card"><div class="stat-label">Weight</div><div class="stat-value">' + (last.weight_lbs ? fmtNum(last.weight_lbs) : '—') + '<small> lbs</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Waist</div><div class="stat-value">'  + (last.waist_in  ? fmtNum(last.waist_in)  : '—') + '<small> in</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Hips</div><div class="stat-value">'   + (last.hips_in   ? fmtNum(last.hips_in)   : '—') + '<small> in</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Chest</div><div class="stat-value">'  + (last.chest_in  ? fmtNum(last.chest_in)  : '—') + '<small> in</small></div></div>';
    html += '</div>';
  }

  if (checkins.some(function(c) { return c.weight_lbs; })) {
    html += '<div class="section-label">Weight trend</div>';
    html += '<div class="card"><div class="card-body" style="height:160px"><canvas id="weight-chart"></canvas></div></div>';
  }

  html += '<div class="section-label" style="margin-top:20px">Log measurements</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Date</label><input type="date" id="ms-date" value="' + today() + '"></div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Weight (lbs)</label><input type="number" id="ms-weight" step="0.1" inputmode="decimal" placeholder="185"></div>';
  html += '<div class="field"><label>Waist (in)</label><input type="number" id="ms-waist" step="0.1" inputmode="decimal" placeholder="34"></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Hips (in)</label><input type="number" id="ms-hips" step="0.1" inputmode="decimal" placeholder="38"></div>';
  html += '<div class="field"><label>Chest (in)</label><input type="number" id="ms-chest" step="0.1" inputmode="decimal" placeholder="40"></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Arms (in)</label><input type="number" id="ms-arms" step="0.1" inputmode="decimal" placeholder="14"></div>';
  html += '<div class="field"><label>Thighs (in)</label><input type="number" id="ms-thighs" step="0.1" inputmode="decimal" placeholder="22"></div>';
  html += '</div>';
  html += '<button class="btn btn-primary" onclick="logMeasurements(' + patientId + ')">Save</button>';
  html += '<div id="ms-flash" class="flash-msg"></div>';
  html += '</div></div>';
  html += '</div>';
  return html;
}

async function logMeasurements(patientId) {
  try {
    await POST('/api/checkins/', {
      date:       document.getElementById('ms-date').value,
      weight_lbs: document.getElementById('ms-weight').value || null,
      waist_in:   document.getElementById('ms-waist').value  || null,
      hips_in:    document.getElementById('ms-hips').value   || null,
      chest_in:   document.getElementById('ms-chest').value  || null,
      arms_in:    document.getElementById('ms-arms').value   || null,
      thighs_in:  document.getElementById('ms-thighs').value || null,
    });
    flash('ms-flash', '✓ Saved');
    loadProgress();
  } catch (err) { flash('ms-flash', err.message, true); }
}








/* ══════════════════════════════════════════
   PROFILE
══════════════════════════════════════════ */
async function loadProfile() {
  const el = document.getElementById('page-profile');
  el.innerHTML = '<div class="empty-state">Loading...</div>';
  try {
    const me      = await GET('/auth/me');
    S.userId      = me.id;
    const profile = await GET('/api/profile/' + me.id);
    renderProfile(el, profile, me.id);
  } catch (err) {
    el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>' + err.message + '</div>';
  }
}

function renderProfile(el, profile, patientId) {
  const name = [profile.first_name, profile.last_name].filter(Boolean).join(' ') || profile.username;
  let html = safetyBanner();

  html += '<div class="profile-hero">';
  html += '<div class="profile-avatar">' + initials(name) + '</div>';
  html += '<div><div class="profile-name">' + name + '</div>';
  html += '<div class="profile-handle">@' + (profile.username || '') + '</div></div>';
  html += '</div>';

  html += '<div class="section">';
  html += '<div class="section-label">Profile</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field-row"><div class="field"><label>First name</label><input type="text" id="prof-first" value="' + (profile.first_name || '') + '" autocapitalize="words"></div>';
  html += '<div class="field"><label>Last name</label><input type="text" id="prof-last" value="' + (profile.last_name || '') + '" autocapitalize="words"></div></div>';
  html += '<div class="field"><label>Email</label><input type="email" id="prof-email" value="' + (profile.email || '') + '" autocapitalize="none"></div>';
  html += '<div class="field"><label>Goals</label><textarea id="prof-goals">' + (profile.goals || '') + '</textarea></div>';
  html += '<button class="btn btn-primary" onclick="saveProfile(' + patientId + ')">Save profile</button>';
  html += '<div id="prof-flash" class="flash-msg"></div>';
  html += '</div></div>';

  html += '<div class="section-label" style="margin-top:16px">Change username</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>New username</label><input type="text" id="new-username" autocapitalize="none" spellcheck="false" placeholder="' + (profile.username || '') + '"></div>';
  html += '<button class="btn btn-primary" onclick="changeUsername()">Update username</button>';
  html += '<div id="username-flash" class="flash-msg"></div>';
  html += '</div></div>';

  html += '<div class="section-label" style="margin-top:16px">Change password</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Current password</label><input type="password" id="cur-pw" autocomplete="current-password"></div>';
  html += '<div class="field-row"><div class="field"><label>New password</label><input type="password" id="new-pw" autocomplete="new-password"></div>';
  html += '<div class="field"><label>Confirm</label><input type="password" id="confirm-pw" autocomplete="new-password"></div></div>';
  html += '<button class="btn btn-primary" onclick="changePassword()">Update password</button>';
  html += '<div id="pw-flash" class="flash-msg"></div>';
  html += '</div></div>';

  html += '<div class="section-label" style="margin-top:16px">Notifications</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Timezone</label>';
  html += '<select id="prof-timezone" onchange="saveTimezone(this.value)">';
  html += '<option value="-5"' + (profile.timezone_offset === -5 ? ' selected' : '') + '>Eastern (UTC-5 / EST)</option>';
  html += '<option value="-4"' + (profile.timezone_offset === -4 ? ' selected' : '') + '>Eastern Daylight (UTC-4 / EDT)</option>';
  html += '<option value="-6"' + (profile.timezone_offset === -6 ? ' selected' : '') + '>Central (UTC-6 / CST)</option>';
  html += '<option value="-7"' + (profile.timezone_offset === -7 ? ' selected' : '') + '>Mountain (UTC-7 / MST)</option>';
  html += '<option value="-8"' + (profile.timezone_offset === -8 ? ' selected' : '') + '>Pacific (UTC-8 / PST)</option>';
  html += '<option value="-9"' + (profile.timezone_offset === -9 ? ' selected' : '') + '>Alaska (UTC-9)</option>';
  html += '<option value="-10"' + (profile.timezone_offset === -10 ? ' selected' : '') + '>Hawaii (UTC-10)</option>';
  html += '<option value="0"' + (profile.timezone_offset === 0 ? ' selected' : '') + '>UTC</option>';
  html += '<option value="1"' + (profile.timezone_offset === 1 ? ' selected' : '') + '>UTC+1</option>';
  html += '<option value="2"' + (profile.timezone_offset === 2 ? ' selected' : '') + '>UTC+2</option>';
  html += '</select></div>';
  html += '<div style="font-size:11px;color:var(--muted);margin:6px 0 14px">Set your timezone so reminders fire at the right local time.</div>';
  html += '<button class="btn btn-primary" onclick="enableNotifications()">Enable push notifications</button>';
  html += '<div id="notif-flash" class="flash-msg"></div>';
  html += '<div id="tz-flash" class="flash-msg"></div>';
  html += '</div></div>';
  html += '<div class="section-label" style="margin-top:16px">Account</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<button class="btn btn-danger" onclick="logout()">Sign out</button>';
  html += '</div></div>';

  html += '</div>';
  el.innerHTML = html;
}

async function saveProfile(patientId) {
  try {
    await PUT('/api/profile/' + patientId, {
      first_name: document.getElementById('prof-first').value.trim() || null,
      last_name:  document.getElementById('prof-last').value.trim()  || null,
      email:      document.getElementById('prof-email').value.trim() || null,
      goals:      document.getElementById('prof-goals').value.trim() || null,
    });
    flash('prof-flash', '✓ Profile saved');
  } catch (err) { flash('prof-flash', err.message, true); }
}

async function saveTimezone(val) {
  try {
    await PUT('/api/profile/' + S.userId, { timezone_offset: parseFloat(val) });
    flash('tz-flash', '✓ Timezone saved');
  } catch (err) { flash('tz-flash', err.message, true); }
}

async function changeUsername() {
  const username = document.getElementById('new-username').value.trim().toLowerCase();
  if (!username) return;
  try {
    const data = await POST('/auth/change-username', { username });
    S.user = data.username;
    flash('username-flash', '✓ Username changed to: ' + data.username);
    document.getElementById('new-username').value       = '';
    document.getElementById('new-username').placeholder = data.username;
  } catch (err) { flash('username-flash', err.message, true); }
}

async function changePassword() {
  const cur  = document.getElementById('cur-pw').value;
  const pw   = document.getElementById('new-pw').value;
  const conf = document.getElementById('confirm-pw').value;
  if (pw !== conf)   { flash('pw-flash', 'Passwords do not match', true); return; }
  if (pw.length < 6) { flash('pw-flash', 'Min 6 characters', true); return; }
  try {
    await POST('/auth/change-password', { current_password: cur, new_password: pw });
    flash('pw-flash', '✓ Password updated');
    document.getElementById('cur-pw').value    = '';
    document.getElementById('new-pw').value    = '';
    document.getElementById('confirm-pw').value = '';
  } catch (err) { flash('pw-flash', err.message, true); }
}

/* ══════════════════════════════════════════
   LEARN TAB
══════════════════════════════════════════ */
const PEPTIDE_CACHE = {};
let HISTORY_OFFSET = 0;
const PD_URLS = {
  '5-amino-1mq': 'https://peptidedosages.com/single-peptide-dosages/5-amino-1mq-10-mg-vial-dosage-protocol/',
  'adamax': 'https://peptidedosages.com/single-peptide-dosages/adamax-10-mg-vial-dosage-protocol/',
  'adipotide': 'https://peptidedosages.com/single-peptide-dosages/adipotide-10-mg-vial-dosage-protocol/',
  'aicar': 'https://peptidedosages.com/single-peptide-dosages/aicar-50-mg-vial-dosage-protocol/',
  'aod-9604': 'https://peptidedosages.com/single-peptide-dosages/aod-9604-5-mg-vial-dosage-protocol/',
  'ara-290': 'https://peptidedosages.com/single-peptide-dosages/ara-290-16-mg-vial-dosage-protocol/',
  'bpc-157': 'https://peptidedosages.com/single-peptide-dosages/bpc-157-5-mg-vial-dosage-protocol/',
  'cagrilintide': 'https://peptidedosages.com/single-peptide-dosages/cagrilintide-5-mg-vial-dosage-protocol/',
  'cartalax': 'https://peptidedosages.com/single-peptide-dosages/cartalax-20-mg-vial-dosage-protocol/',
  'cerebrolysin': 'https://peptidedosages.com/single-peptide-dosages/cerebrolysin-60-mg-vial-dosage-protocol/',
  'chonluten': 'https://peptidedosages.com/single-peptide-dosages/chonluten-20-mg-vial-dosage-protocol/',
  'cjc-1295': 'https://peptidedosages.com/single-peptide-dosages/cjc-1295-no-dac-5-mg-vial-dosage-protocol/',
  'cjc-1295 dac': 'https://peptidedosages.com/single-peptide-dosages/cjc-1295-dac-2-mg-vial-dosage-protocol/',
  'cortagen': 'https://peptidedosages.com/single-peptide-dosages/cortagen-20-mg-vial-dosage-protocol/',
  'dsip': 'https://peptidedosages.com/single-peptide-dosages/dsip-5-mg-vial-dosage-protocol/',
  'epitalon': 'https://peptidedosages.com/single-peptide-dosages/epitalon-epithalon-10-mg-vial-dosage-protocol/',
  'epithalon': 'https://peptidedosages.com/single-peptide-dosages/epitalon-epithalon-10-mg-vial-dosage-protocol/',
  'foxo4-dri': 'https://peptidedosages.com/single-peptide-dosages/foxo4-dri-10-mg-vial-dosage-protocol/',
  'ghk-cu': 'https://peptidedosages.com/single-peptide-dosages/ghk-cu-50-mg-vial-dosage-protocol/',
  'ghrp-2': 'https://peptidedosages.com/single-peptide-dosages/ghrp-2-5-mg-vial-dosage-protocol/',
  'ghrp-6': 'https://peptidedosages.com/single-peptide-dosages/ghrp-6-5-mg-vial-dosage-protocol/',
  'glutathione': 'https://peptidedosages.com/single-peptide-dosages/glutathione-600-mg-vial-dosage-protocol/',
  'gonadorelin': 'https://peptidedosages.com/single-peptide-dosages/gonadorelin-2-mg-vial-dosage-protocol/',
  'hcg': 'https://peptidedosages.com/single-peptide-dosages/hcg-5000-iu-vial-dosage-protocol/',
  'hgh 191aa': 'https://peptidedosages.com/single-peptide-dosages/hgh-191aa-10-iu-vial-dosage-protocol/',
  'hmg': 'https://peptidedosages.com/single-peptide-dosages/hmg-75-iu-vial-dosage-protocol/',
  'igf-1 lr3': 'https://peptidedosages.com/single-peptide-dosages/igf-1-lr3-1-mg-vial-dosage-protocol/',
  'ipamorelin': 'https://peptidedosages.com/single-peptide-dosages/ipamorelin-5-mg-vial-dosage-protocol/',
  'kisspeptin': 'https://peptidedosages.com/single-peptide-dosages/kisspeptin-10-mg-vial-dosage-protocol/',
  'kisspeptin-10': 'https://peptidedosages.com/single-peptide-dosages/kisspeptin-10-mg-vial-dosage-protocol/',
  'kpv': 'https://peptidedosages.com/single-peptide-dosages/kpv-10-mg-vial-dosage-protocol/',
  'l-carnitine': 'https://peptidedosages.com/single-peptide-dosages/l-carnitine-200-mg-vial-dosage-protocol/',
  'livagen': 'https://peptidedosages.com/single-peptide-dosages/livagen-20-mg-vial-dosage-protocol/',
  'll-37': 'https://peptidedosages.com/single-peptide-dosages/ll-37-5-mg-vial-dosage-protocol/',
  'mazdutide': 'https://peptidedosages.com/single-peptide-dosages/mazdutide-5-mg-vial-dosage-protocol/',
  'melanotan ii': 'https://peptidedosages.com/single-peptide-dosages/melanotan-ii-10-mg-vial-dosage-protocol/',
  'mgf': 'https://peptidedosages.com/single-peptide-dosages/mgf-5-mg-vial-dosage-protocol/',
  'mots-c': 'https://peptidedosages.com/single-peptide-dosages/mots-c-5-mg-vial-dosage-protocol/',
  'nad+': 'https://peptidedosages.com/single-peptide-dosages/nad-500-mg-10ml-vial-dosage-protocol/',
  'ovagen': 'https://peptidedosages.com/single-peptide-dosages/ovagen-20-mg-vial-dosage-protocol/',
  'oxytocin': 'https://peptidedosages.com/single-peptide-dosages/oxytocin-5-mg-vial-dosage-protocol/',
  'pe-22-28': 'https://peptidedosages.com/single-peptide-dosages/pe-22-28-10-mg-vial-dosage-protocol/',
  'peg mgf': 'https://peptidedosages.com/single-peptide-dosages/peg-mgf-2-mg-vial-dosage-protocol/',
  'pegylated mgf': 'https://peptidedosages.com/single-peptide-dosages/peg-mgf-2-mg-vial-dosage-protocol/',
  'pinealon': 'https://peptidedosages.com/single-peptide-dosages/pinealon-20-mg-vial-dosage-protocol/',
  'pnc-27': 'https://peptidedosages.com/single-peptide-dosages/pnc-27-30-mg-vial-dosage-protocol/',
  'prostamax': 'https://peptidedosages.com/single-peptide-dosages/prostamax-20-mg-vial-dosage-protocol/',
  'pt-141': 'https://peptidedosages.com/single-peptide-dosages/pt-141-10-mg-vial-dosage-protocol/',
  'retatrutide': 'https://peptidedosages.com/single-peptide-dosages/retatrutide-5-mg-vial-dosage-protocol/',
  'selank': 'https://peptidedosages.com/single-peptide-dosages/selank-5-mg-vial-dosage-protocol/',
  'semaglutide': 'https://peptidedosages.com/single-peptide-dosages/semaglutide-5-mg-vial-dosage-protocol/',
  'semax': 'https://peptidedosages.com/single-peptide-dosages/semax-5-mg-vial-dosage-protocol/',
  'sermorelin': 'https://peptidedosages.com/single-peptide-dosages/sermorelin-5-mg-vial-dosage-protocol/',
  'slu-pp-332': 'https://peptidedosages.com/single-peptide-dosages/slu-pp-332-5-mg-vial-dosage-protocol/',
  'snap-8': 'https://peptidedosages.com/single-peptide-dosages/snap-8-10-mg-vial-dosage-protocol/',
  'ss-31': 'https://peptidedosages.com/single-peptide-dosages/ss-31-10-mg-vial-dosage-protocol/',
  'survodutide': 'https://peptidedosages.com/single-peptide-dosages/survodutide-10-mg-vial-dosage-protocol/',
  'tb-4 frag': 'https://peptidedosages.com/single-peptide-dosages/tb-500-5-mg-vial-dosage-protocol/',
  'tb-500': 'https://peptidedosages.com/single-peptide-dosages/tb-500-5-mg-vial-dosage-protocol/',
  'tesamorelin': 'https://peptidedosages.com/single-peptide-dosages/tesamorelin-5-mg-vial-dosage-protocol/',
  'testagen': 'https://peptidedosages.com/single-peptide-dosages/testagen-20-mg-vial-dosage-protocol/',
  'thymosin alpha-1': 'https://peptidedosages.com/single-peptide-dosages/thymosin-alpha-1-5-mg-vial-dosage-protocol/',
  'thymosin beta-4': 'https://peptidedosages.com/single-peptide-dosages/tb-500-5-mg-vial-dosage-protocol/',
  'tirzepatide': 'https://peptidedosages.com/single-peptide-dosages/tirzepatide-5-mg-vial-dosage-protocol/',
  'vesugen': 'https://peptidedosages.com/single-peptide-dosages/vesugen-20-mg-vial-dosage-protocol/',
  'vilon': 'https://peptidedosages.com/single-peptide-dosages/vilon-20-mg-vial-dosage-protocol/',
};
let PEPTIDE_DOSAGE_DATA = {};  // loaded from static JSON

async function loadPeptideDosageData() {
  try {
    const resp = await fetch('/static/peptide_data.json');
    const arr  = await resp.json();
    arr.forEach(function(p) { PEPTIDE_DOSAGE_DATA[p.name.toLowerCase()] = p; });
  } catch (e) { console.warn('Could not load peptide_data.json', e); }
}

function loadLearn() {
  const el = document.getElementById('page-learn');
  let html = safetyBanner();
  html += '<div class="inner-tabs">';
  html += '<button class="inner-tab active" id="learn-tab-library"  onclick="switchLearnTab(\'library\', this)">Library</button>';
  html += '<button class="inner-tab"        id="learn-tab-videos"   onclick="switchLearnTab(\'videos\', this)">Videos</button>';
  html += '<button class="inner-tab"        id="learn-tab-vendors"  onclick="switchLearnTab(\'vendors\', this)">Vendors</button>';
  html += '<button class="inner-tab"        id="learn-tab-vendors"  onclick="switchLearnTab(\'vendors\', this)">COA</button>';
  html += '</div>';
  html += '<div class="inner-panel active" id="learn-library">';
  html += renderLibraryPanel();
  html += '</div>';

  html += '<div class="inner-panel" id="learn-videos">';
  html += renderVideosPanel();
  html += '</div>';
  html += '<div class="inner-panel" id="learn-vendors">';
  html += renderVendorsPanel();
  html += '</div>';
  el.innerHTML = html;
}

function switchLearnTab(name, btn) {
  document.querySelectorAll('#page-learn .inner-tab').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('#page-learn .inner-panel').forEach(function(p) { p.classList.remove('active'); });
  btn.classList.add('active');
  const panel = document.getElementById('learn-' + name);
  if (panel) panel.classList.add('active');
}

function renderVideosPanel() {
  const videos = [
    { id: 'KQJxfVAsXfA', title: 'Reconstitution Guide 1' },
    { id: 'vDj669U5VmA', title: 'Reconstitution Guide 2' },
    { id: 'tcEWjyQfDLc', title: 'Reconstitution Guide 3' },
    { id: 'L65S1xmKY44', title: 'Reconstitution Guide 4' },
    { id: 'b08QwxZW0Ig', title: 'Reconstitution Guide 5' },
  ];
  let html = '<div class="videos-list">';
  videos.forEach(function(v) {
    html += '<div class="video-card">';
    html += '<div class="video-title">' + v.title + '</div>';
    html += '<div class="video-embed-wrap">';
    html += '<iframe src="https://www.youtube.com/embed/' + v.id + '" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" loading="lazy"></iframe>';
    html += '</div></div>';
  });
  html += '</div>';
  return html;
}

function toSlug(str) {
  return str.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-');
}

function renderVendorsPanel() {
  let html = '<div class="vendors-wrap">';

  html += '<div class="vendor-actions">';
  html += '<a href="https://www.finnrick.com/verify" target="_blank" class="vendor-action-btn vendor-action-primary">🔍 Verify a COA</a>';
  html += '<a href="https://www.finnrick.com/vendors" target="_blank" class="vendor-action-btn">📋 Browse all 217+ vendors</a>';
  html += '<a href="https://www.finnrick.com/products" target="_blank" class="vendor-action-btn">💊 Browse by peptide</a>';
  html += '</div>';

  html += '<div class="vendor-search-block">';
  html += '<div class="vendor-search-label">Look up a compound on Finnrick</div>';
  html += '<div class="vendor-search-row">';
  html += '<input type="text" id="coa-compound-input" class="library-search" placeholder="e.g. BPC-157, Semaglutide…" style="flex:1">';
  html += '<button class="coa-search-btn" onclick="searchCOAByCompound()">Go →</button>';
  html += '</div></div>';

  html += '<div class="vendor-search-block">';
  html += '<div class="vendor-search-label">Look up a vendor on Finnrick</div>';
  html += '<div class="vendor-search-row">';
  html += '<input type="text" id="coa-vendor-input" class="library-search" placeholder="Vendor name…" style="flex:1">';
  html += '<button class="coa-search-btn" onclick="searchCOAByVendor()">Go →</button>';
  html += '</div></div>';

  html += '<div style="font-size:11px;color:var(--muted);padding:8px 20px 20px;text-align:center">Powered by <a href="https://www.finnrick.com" target="_blank" style="color:var(--accent)">Finnrick.com</a> — 8,900+ tests across 217+ vendors</div>';
  html += '</div>';
  return html;
}

function searchCOAByCompound() {
  const val = document.getElementById('coa-compound-input').value.trim();
  if (!val) return;
  window.open('https://www.finnrick.com/products/' + toSlug(val), '_blank');
}

function searchCOAByVendor() {
  const val = document.getElementById('coa-vendor-input').value.trim();
  if (!val) return;
  window.open('https://www.finnrick.com/vendors/' + toSlug(val), '_blank');
}

function openVendorCOA(vendorName) {
  window.open('https://www.finnrick.com/vendors/' + toSlug(vendorName), '_blank');
}

function filterVendorList(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.vendor-chip').forEach(function(btn) {
    btn.style.display = btn.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function renderLibraryPanel() {
  const peptides = [
    '5-Amino-1MQ','ACE-031','ACTH','ANP','AOD-9604','ARA-290',
    'Abaloparatide','Afamelanotide','Albiglutide','Alpha-MSH','Angiotensin 1-7',
    'Argireline','BDNF','BMP-2','BMP-7','BNP','BPC-157','Bradykinin',
    'Bremelanotide','Buserelin','CJC-1295','CJC-1295 DAC','CRH','Calcitonin',
    'Carcinine','Carnosine','Cerebrolysin','Cetrorelix','Colivelin',
    'Copper Peptide','Cortagen','DSIP','Degarelix','Desmopressin','Dihexa',
    'Dulaglutide','EGF','Epitalon','Epithalon','Exenatide','Follistatin 344',
    'Follitropin Alpha','Fragment 176-191','GHK','GHK-Cu','GHRH','GHRP-2',
    'GHRP-6','GIP','GLP-1','Ganirelix','Ghrelin','Gonadorelin','Goserelin',
    'Hexarelin','Humanin','IGF-1','IGF-1 DES','IGF-1 LR3','IGF-2',
    'Ibutamoren','Ipamorelin','KPV','Kisspeptin-10','Kisspeptin-54','Klotho',
    'LL-37','Larazotide','Leptin','Leuphasyl','Leuprolide','Liraglutide',
    'Lutropin Alpha','MCH','MGF','MK-677','MOTS-c','Matrixyl',
    'Mechano Growth Factor','Melanotan I','Melanotan II','Mod GRF 1-29',
    'N-Acetyl Epithalon Amidate','NAD+','NGF','Nafarelin','Nesiritide',
    'Neuropeptide Y','Obestatin','Orexin A','Orexin B','Oxyntomodulin',
    'Oxytocin','P21','PACAP','PDA','PEG-MGF','PT-141','PYY 3-36',
    'Palmitoyl Pentapeptide-4','Pinealon','Pramlintide','Retatrutide',
    'SS-31','Secretin','Selank','Semaglutide','Semax','Sermorelin',
    'Snap-8','Substance P','TA-1','TB-4 Frag','TB-500','Teriparatide',
    'Tesamorelin','Thymalin','Thymogen','Thymosin Alpha-1','Thymosin Beta-4',
    'Thymulin','Tirzepatide','Triptorelin','VIP','Vilon','Vosoritide','hCG',
  ].filter(function(v, i, a) { return a.indexOf(v) === i; });

  let html = '<div class="library-search-wrap">';
  html += '<input type="text" id="library-search" class="library-search" placeholder="Search peptides…" oninput="filterLibrary(this.value)">';
  html += '</div>';
  html += '<div class="library-grid" id="library-grid">';
  peptides.forEach(function(name) {
    html += '<button class="peptide-chip" onclick="openPeptideCard(\'' + name + '\')">';
    html += '<span class="peptide-chip-name">' + name + '</span>';
    html += '<span class="peptide-chip-arrow">→</span>';
    html += '</button>';
  });
  html += '</div>';
  html += '<div id="peptide-card-container"></div>';
  return html;
}

function filterLibrary(query) {
  const q    = query.toLowerCase();
  const btns = document.querySelectorAll('.peptide-chip');
  btns.forEach(function(btn) {
    const name = btn.querySelector('.peptide-chip-name').textContent.toLowerCase();
    btn.style.display = name.includes(q) ? '' : 'none';
  });
}

async function openPeptideCard(peptideName) {
  const container = document.getElementById('peptide-card-container');
  if (!container) return;

  // Check cache
  if (PEPTIDE_CACHE[peptideName]) {
    renderPeptideCard(container, peptideName, PEPTIDE_CACHE[peptideName]);
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }

  // Check static dosage data first — show immediately
  const staticData = PEPTIDE_DOSAGE_DATA[peptideName.toLowerCase()];
  if (staticData) {
    const quickInfo = {
      dosing:    staticData.dosage,
      frequency: staticData.frequency,
      route:     staticData.route,
      notes:     staticData.notes,
      mechanism: 'Loading additional details…',
      uses:      [],
      halfLife:  '—',
      sideEffects: [],
      stacks:    [],
    };
    renderPeptideCard(container, peptideName, quickInfo);
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } else {
    container.innerHTML = '<div class="peptide-card-loading"><div class="peptide-card-spinner"></div><div style="color:var(--muted);font-size:13px;margin-top:12px">Loading ' + peptideName + '…</div></div>';
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Fetch AI enrichment (mechanism, uses, stacks, side effects)
  try {
    const info = await POST('/api/learn/peptide', { name: peptideName });
    // Merge: prefer static dosage data over AI for dosing fields
    if (staticData) {
      info.dosing    = staticData.dosage    || info.dosing;
      info.frequency = staticData.frequency || info.frequency;
      info.route     = staticData.route     || info.route;
      if (staticData.notes) {
        info.reconstitution = staticData.notes;
      }
    }
    PEPTIDE_CACHE[peptideName] = info;
    renderPeptideCard(container, peptideName, info);
  } catch (err) {
    if (!staticData) {
      container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div>Could not load data for ' + peptideName + '.<br><small>' + err.message + '</small></div>';
    }
    // If we already showed static data, leave it up even if AI call failed
  }
}

function renderPeptideCard(container, name, info) {
  let html = '<div class="peptide-card">';
  html += '<div class="peptide-card-header">';
  html += '<div class="peptide-card-name">' + name + '</div>';
  html += '<button class="peptide-card-close" onclick="closePeptideCard()">✕</button>';
  html += '</div>';

  html += '<div class="peptide-card-section">';
  html += '<div class="peptide-card-label">Mechanism</div>';
  html += '<div class="peptide-card-text">' + (info.mechanism || '—') + '</div>';
  html += '</div>';

  if (info.uses && info.uses.length) {
    html += '<div class="peptide-card-section">';
    html += '<div class="peptide-card-label">Common uses</div>';
    html += '<div class="peptide-tags">';
    info.uses.forEach(function(u) { html += '<span class="peptide-tag">' + u + '</span>'; });
    html += '</div></div>';
  }

  html += '<div class="peptide-card-grid">';
  html += '<div class="peptide-card-stat"><div class="peptide-card-stat-label">Typical dose</div><div class="peptide-card-stat-val">' + (info.dosing || '—') + '</div></div>';
  html += '<div class="peptide-card-stat"><div class="peptide-card-stat-label">Frequency</div><div class="peptide-card-stat-val">' + (info.frequency || '—') + '</div></div>';
  html += '<div class="peptide-card-stat"><div class="peptide-card-stat-label">Route</div><div class="peptide-card-stat-val">' + (info.route || '—') + '</div></div>';
  html += '<div class="peptide-card-stat"><div class="peptide-card-stat-label">Half-life</div><div class="peptide-card-stat-val">' + (info.halfLife || '—') + '</div></div>';
  html += '</div>';

  if (info.reconstitution) {
    html += '<div class="peptide-card-section">';
    html += '<div class="peptide-card-label">Reconstitution</div>';
    html += '<div class="peptide-card-text">' + info.reconstitution + '</div>';
    html += '</div>';
  }

  if (info.sideEffects && info.sideEffects.length) {
    html += '<div class="peptide-card-section">';
    html += '<div class="peptide-card-label">Side effects</div>';
    html += '<div class="peptide-tags">';
    info.sideEffects.forEach(function(s) { html += '<span class="peptide-tag peptide-tag-warn">' + s + '</span>'; });
    html += '</div></div>';
  }

  if (info.stacks && info.stacks.length) {
    html += '<div class="peptide-card-section">';
    html += '<div class="peptide-card-label">Common stacks</div>';
    html += '<div class="peptide-tags">';
    info.stacks.forEach(function(s) { html += '<span class="peptide-tag peptide-tag-accent">' + s + '</span>'; });
    html += '</div></div>';
  }

  const pdUrl = PD_URLS[name.toLowerCase()] || ('https://peptidedosages.com/single-peptide-dosages/?s=' + encodeURIComponent(name));
  html += '<div style="border-top:1px solid var(--border);margin-top:8px;padding:12px 0;display:flex;align-items:center;justify-content:space-between;gap:12px">';
  html += '<div style="font-size:11px;color:var(--muted);font-style:italic">Educational reference only.</div>';
  html += '<a href="' + pdUrl + '" target="_blank" style="font-size:12px;font-weight:700;color:var(--accent);text-decoration:none;white-space:nowrap">Full protocol →</a>';
  html += '</div>';
  html += '</div>';
  container.innerHTML = html;
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function closePeptideCard() {
  const container = document.getElementById('peptide-card-container');
  if (container) container.innerHTML = '';
}



/* ══════════════════════════════════════════
   DOSE CALCULATOR
══════════════════════════════════════════ */
function loadCalc() {
  const el = document.getElementById('page-calc');
  el.innerHTML =
    safetyBanner() +
    '<div class="section">' +
    '<div class="section-label">Reconstitution calculator</div>' +
    '<div class="card"><div class="card-body">' +

    '<div class="field-row">' +
    '<div class="field" style="flex:2"><label id="calc-vial-label">Vial size (mg)</label>' +
    '<input type="number" id="calc-vial" step="0.1" inputmode="decimal" placeholder="5" oninput="runCalc()"></div>' +
    '<div class="field" style="flex:1"><label>Unit</label>' +
    '<select id="calc-unit" onchange="updateCalcLabels();runCalc()"><option>mg</option><option>mcg</option><option>IU</option><option>g</option></select></div>' +
    '</div>' +

    '<div class="field"><label>Bacteriostatic water added (mL)</label>' +
    '<input type="number" id="calc-water" step="0.1" inputmode="decimal" placeholder="2" oninput="runCalc()"></div>' +

    '<div class="field"><label id="calc-dose-label">Desired dose (mg)</label>' +
    '<input type="number" id="calc-dose" step="0.01" inputmode="decimal" placeholder="0.5" oninput="runCalc()"></div>' +

    '</div></div>' +

    '<div id="calc-result" style="display:none">' +
    '<div class="card"><div class="card-body">' +

    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid var(--border)">' +
    '<div><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Concentration</div>' +
    '<div style="font-family:var(--mono);font-size:22px;font-weight:700" id="calc-conc">—</div></div>' +
    '<div style="text-align:right"><div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Volume</div>' +
    '<div style="font-family:var(--mono);font-size:22px;font-weight:700" id="calc-ml">—</div></div>' +
    '</div>' +

    '<div style="text-align:center;padding:16px 0">' +
    '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:10px">Draw to this line on insulin syringe</div>' +
    '<div style="font-family:var(--mono);font-size:56px;font-weight:700;color:var(--accent);line-height:1" id="calc-units">—</div>' +
    '<div style="font-family:var(--mono);font-size:16px;color:var(--muted);margin-top:4px">units</div>' +
    '</div>' +

    '<div style="display:flex;justify-content:center;padding:12px 0 4px;border-top:1px solid var(--border);margin-top:8px">' +
    '<div style="text-align:center">' +
    '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:6px">Doses per vial</div>' +
    '<div style="font-family:var(--mono);font-size:36px;font-weight:700;color:var(--green);line-height:1" id="calc-doses">—</div>' +
    '<div style="font-family:var(--mono);font-size:14px;color:var(--muted);margin-top:4px">doses</div>' +
    '</div></div>' +

    '</div></div></div>' +

    '<div class="card" style="margin-top:4px"><div class="card-body" style="padding:14px 16px">' +
    '<div style="font-size:11px;color:var(--muted);line-height:1.7">' +
    '<strong style="color:var(--text)">How to use:</strong><br>' +
    '1. Enter your vial size (printed on the vial)<br>' +
    '2. Enter how much bac water you added<br>' +
    '3. Enter your prescribed dose<br>' +
    '4. Draw to the unit number shown above' +
    '</div></div></div>' +

    '</div>';
}

function updateCalcLabels() {
  const unit = document.getElementById('calc-unit') ? document.getElementById('calc-unit').value : 'mg';
  const vl   = document.getElementById('calc-vial-label');
  const dl   = document.getElementById('calc-dose-label');
  if (vl) vl.textContent = 'Vial size (' + unit + ')';
  if (dl) dl.textContent = 'Desired dose (' + unit + ')';
}

function runCalc() {
  const vial  = parseFloat(document.getElementById('calc-vial').value);
  const water = parseFloat(document.getElementById('calc-water').value);
  const dose  = parseFloat(document.getElementById('calc-dose').value);
  const res   = document.getElementById('calc-result');

  if (!vial || !water || !dose || water <= 0 || vial <= 0 || dose <= 0) {
    if (res) res.style.display = 'none';
    return;
  }

  const conc  = vial / water;
  const ml    = dose / conc;
  const units = Math.round(ml * 100 * 10) / 10;

  const unit = document.getElementById('calc-unit') ? document.getElementById('calc-unit').value : 'mg';
  const dosesInVial = Math.floor(vial / dose);
  document.getElementById('calc-conc').textContent  = conc.toFixed(unit === 'IU' ? 0 : 2) + ' ' + unit + '/mL';
  document.getElementById('calc-ml').textContent    = ml.toFixed(3) + ' mL';
  document.getElementById('calc-units').textContent = units.toFixed(1);
  document.getElementById('calc-doses').textContent = dosesInVial;
  res.style.display = 'block';
}

/* ══════════════════════════════════════════
   ONBOARDING
══════════════════════════════════════════ */
function showOnboarding(profile) {
  onboardStep = 1;
  document.getElementById('onboarding-modal').style.display = 'flex';
  renderOnboardStep(profile);
}

function renderOnboardStep(profile) {
  const total   = 4;
  const num     = document.getElementById('onboard-step-num');
  const fill    = document.getElementById('onboard-fill');
  const backBtn = document.getElementById('onboard-back-btn');
  const nextBtn = document.getElementById('onboard-next-btn');
  const content = document.getElementById('onboard-content');

  num.textContent       = '0' + onboardStep + ' / 0' + total;
  fill.style.width      = (onboardStep / total * 100) + '%';
  backBtn.style.display = onboardStep > 1 ? 'block' : 'none';
  nextBtn.textContent   = onboardStep === total ? 'Get started' : 'Continue';

  const steps = {
    1: '<div class="onboard-title">Welcome 👋</div><div class="onboard-sub">Let\'s set up your profile. It only takes a minute.</div>' +
       '<div class="field-row"><div class="field"><label>First name</label><input type="text" id="ob-first" value="' + (profile.first_name || '') + '" autocapitalize="words"></div>' +
       '<div class="field"><label>Last name</label><input type="text" id="ob-last" value="' + (profile.last_name || '') + '" autocapitalize="words"></div></div>',

    2: '<div class="onboard-title">About you</div><div class="onboard-sub">This helps personalize your experience.</div>' +
       '<div class="field-row"><div class="field"><label>Date of birth</label><input type="date" id="ob-dob" value="' + (profile.date_of_birth || '') + '"></div>' +
       '<div class="field"><label>Sex</label><select id="ob-sex"><option value="">Select</option><option value="Male"' + (profile.sex === 'Male' ? ' selected' : '') + '>Male</option><option value="Female"' + (profile.sex === 'Female' ? ' selected' : '') + '>Female</option></select></div></div>' +
       '<div class="field"><label>Height (e.g. 5ft 11in or 71)</label><input type="text" id="ob-height" value="' + (profile.height_in ? Math.floor(profile.height_in / 12) + 'ft ' + Math.round(profile.height_in % 12) + 'in' : '') + '" placeholder="5ft 10in"></div>',

    3: '<div class="onboard-title">Starting weight</div><div class="onboard-sub">We\'ll track your progress from here.</div>' +
       '<div class="field"><label>Weight (lbs)</label><input type="number" id="ob-weight" step="0.1" inputmode="decimal" placeholder="185"></div>',

    4: '<div class="onboard-title">Your goals</div><div class="onboard-sub">What are you hoping to achieve? Your practitioner will see this too.</div>' +
       '<div class="field"><label>Goals</label><textarea id="ob-goals" rows="4" placeholder="e.g. Lose 20 lbs, improve energy and sleep, build lean muscle...">' + (profile.goals || '') + '</textarea></div>',
  };

  content.innerHTML = steps[onboardStep];
}

async function onboardNext() {
  try {
    const me = await GET('/auth/me');
    const id = me.id;

    if (onboardStep === 1) {
      const first = document.getElementById('ob-first').value.trim();
      const last  = document.getElementById('ob-last').value.trim();
      if (first || last) await PUT('/api/profile/' + id, { first_name: first, last_name: last });

    } else if (onboardStep === 2) {
      const dob   = document.getElementById('ob-dob').value || null;
      const sex   = document.getElementById('ob-sex').value || null;
      const htVal = document.getElementById('ob-height').value.trim();
      const dta   = { date_of_birth: dob, sex };
      if (htVal) {
        const m1 = htVal.match(/(\d+)\s*(?:ft|feet)\s*(\d+)/i);
        const m2 = htVal.match(/^([0-9.]+)$/);
        if (m1)      dta.height_in = parseFloat(m1[1]) * 12 + parseFloat(m1[2]);
        else if (m2) dta.height_in = parseFloat(m2[1]);
      }
      await PUT('/api/profile/' + id, dta);

    } else if (onboardStep === 3) {
      const weight = document.getElementById('ob-weight').value;
      if (weight) await POST('/api/profile/' + id + '/weight', { date: today(), weight_lbs: parseFloat(weight) });

    } else if (onboardStep === 4) {
      const goals = document.getElementById('ob-goals').value.trim();
      if (goals) await PUT('/api/profile/' + id, { goals });
      await POST('/api/profile/onboarding-complete', {});
      document.getElementById('onboarding-modal').style.display = 'none';
      const profile = await GET('/api/profile/' + id);
      const name = [profile.first_name, profile.last_name].filter(Boolean).join(' ') || S.user;
      document.getElementById('topbar-name').textContent = name;
      return;
    }

    onboardStep++;
    const profile = await GET('/api/profile/' + id);
    renderOnboardStep(profile);
  } catch (err) { console.error(err); }
}

function onboardBack() {
  if (onboardStep > 1) {
    onboardStep--;
    GET('/auth/me').then(function(me) {
      GET('/api/profile/' + me.id).then(function(p) { renderOnboardStep(p); });
    });
  }
}

async function skipOnboarding() {
  try { await POST('/api/profile/onboarding-complete', {}); } catch (e) {}
  document.getElementById('onboarding-modal').style.display = 'none';
}

/* ══════════════════════════════════════════
   PUSH NOTIFICATIONS
══════════════════════════════════════════ */
async function enableNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    flash('notif-flash', 'Push notifications not supported on this device', true);
    return;
  }
  try {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      flash('notif-flash', 'Permission denied — enable in Settings', true);
      return;
    }
    const reg = await navigator.serviceWorker.ready;
    const keyData = await GET('/api/push/vapid-public-key');
    if (!keyData.key) { flash('notif-flash', 'Server config error', true); return; }
    let sub = await reg.pushManager.getSubscription();
    if (sub) await sub.unsubscribe();
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(keyData.key),
    });
    await savePushSubscription(sub);
    flash('notif-flash', '✓ Notifications enabled!');
  } catch (err) {
    flash('notif-flash', err.message, true);
  }
}

async function initPushNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
  try {
    const reg      = await navigator.serviceWorker.ready;
    const existing = await reg.pushManager.getSubscription();
    if (existing) { await savePushSubscription(existing); return; }
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return;
    const keyData = await GET('/api/push/vapid-public-key');
    if (!keyData.key) return;
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly:      true,
      applicationServerKey: urlBase64ToUint8Array(keyData.key),
    });
    await savePushSubscription(sub);
  } catch (e) {}
}

async function savePushSubscription(sub) {
  const s = sub.toJSON();
  await POST('/api/push/subscribe', { endpoint: s.endpoint, keys: { p256dh: s.keys.p256dh, auth: s.keys.auth } }).catch(function() {});
}

function urlBase64ToUint8Array(base64) {
  const pad = '='.repeat((4 - base64.length % 4) % 4);
  const b64 = (base64 + pad).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(b64);
  return Uint8Array.from([...raw].map(function(c) { return c.charCodeAt(0); }));
}

/* ══════════════════════════════════════════
   RESET TOKEN CHECK
══════════════════════════════════════════ */
(function() {
  const token = new URLSearchParams(window.location.search).get('token');
  if (token && window.location.pathname === '/reset-password') {
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('reset-screen').style.display = 'flex';
      document.getElementById('auth-screen').classList.add('hidden');
    });
  } else if (window.location.pathname !== '/') {
    window.history.replaceState({}, '', '/');
  }
})();

/* ══════════════════════════════════════════
   BOOT
══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function() {
  checkAuth();
  ['auth-username', 'auth-password'].forEach(function(id) {
    const el = document.getElementById(id);
    if (el) el.addEventListener('keydown', function(e) { if (e.key === 'Enter') authSubmit(); });
  });
  // Close dose modal on backdrop click
  const modal = document.getElementById('dose-modal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeDoseModal();
    });
  }
  // Close edit log modal on backdrop click
  const elModal = document.getElementById('edit-log-modal');
  if (elModal) {
    elModal.addEventListener('click', function(e) {
      if (e.target === elModal) closeEditLog();
    });
  }
  // Edit compound modal: no backdrop close (day buttons need multiple taps)
  // Close edit protocol modal on backdrop click
  const epModal = document.getElementById('edit-protocol-modal');
  if (epModal) {
    epModal.addEventListener('click', function(e) {
      if (e.target === epModal) closeEditProtocolModal();
    });
  }
  var apdModal = document.getElementById('add-past-dose-modal');
  if (apdModal) {
    apdModal.addEventListener('click', function(e) {
      if (e.target === apdModal) closeAddPastDoseModal();
    });
  }
});
