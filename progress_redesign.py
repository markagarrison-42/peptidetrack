c = open('/home/madfella/peptidetrack/static/app.js').read()
lines = c.split('\n')

start_progress = None
end_render_body = None
for i, l in enumerate(lines):
    if l.startswith('function renderProgress('):
        start_progress = i
    if l.startswith('async function logMeasurements('):
        end_render_body = i
        break

assert start_progress is not None and end_render_body is not None, "boundaries not found, aborting"

new_block = '''function renderProgress(el, checkins, photos, patientId) {
  let html = safetyBanner();
  html += '<button class="btn btn-ghost" style="margin:0 20px 12px" onclick="showReport()">Print / Save Report</button>';
  html += '<div class="inner-tabs">';
  html += '<button class="inner-tab active" onclick="switchProgressTab(\\'measurements\\', this)">Measurements</button>';
  html += '<button class="inner-tab" onclick="switchProgressTab(\\'vitals\\', this)">Vitals</button>';
  html += '</div>';
  html += '<div class="inner-panel active" id="prog-measurements">';
  html += renderMeasurementsPanel(checkins, patientId);
  html += '</div>';
  html += '<div class="inner-panel" id="prog-vitals">';
  html += renderVitalsPanel(checkins, patientId);
  html += '</div>';
  el.innerHTML = html;
  initMeasurementCharts(checkins);
}

function initMeasurementCharts(checkins) {
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

  const bfData = checkins.filter(function(c) { return c.body_fat_pct; }).slice().reverse().slice(-20);
  if (bfData.length > 1) {
    setTimeout(function() {
      const canvas = document.getElementById('bodyfat-chart');
      if (!canvas) return;
      new Chart(canvas, {
        type: 'line',
        data: {
          labels:   bfData.map(function(c) { return fmtDateShort(c.date); }),
          datasets: [{
            data:               bfData.map(function(c) { return c.body_fat_pct; }),
            borderColor:        '#7c5fe6',
            borderWidth:        2,
            pointRadius:        3,
            pointBackgroundColor: '#7c5fe6',
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
  if (name === 'measurements') initMeasurementCharts(S.checkins || []);
}

function renderMeasurementsPanel(checkins, patientId) {
  const last = checkins[0];
  let html = '<div style="padding:20px">';
  if (last) {
    html += '<div class="section-label">Latest measurements</div>';
    html += '<div class="stat-grid">';
    html += '<div class="stat-card"><div class="stat-label">Weight</div><div class="stat-value">' + (last.weight_lbs ? fmtNum(last.weight_lbs) : '\\u2014') + '<small> lbs</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Waist</div><div class="stat-value">' + (last.waist_in ? fmtNum(last.waist_in) : '\\u2014') + '<small> in</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Chest</div><div class="stat-value">' + (last.chest_in ? fmtNum(last.chest_in) : '\\u2014') + '<small> in</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Body fat</div><div class="stat-value">' + (last.body_fat_pct ? fmtNum(last.body_fat_pct) : '\\u2014') + '<small> %</small></div></div>';
    html += '</div>';
  }
  if (checkins.some(function(c) { return c.weight_lbs; })) {
    html += '<div class="section-label" style="margin-top:20px">Weight trend</div>';
    html += '<div class="card"><div class="card-body" style="height:160px"><canvas id="weight-chart"></canvas></div></div>';
  }
  if (checkins.some(function(c) { return c.body_fat_pct; })) {
    html += '<div class="section-label" style="margin-top:20px">Body fat trend</div>';
    html += '<div class="card"><div class="card-body" style="height:160px"><canvas id="bodyfat-chart"></canvas></div></div>';
  }
  var histRows = checkins.filter(function(c){ return c.weight_lbs||c.neck_in||c.chest_in||c.arms_in||c.waist_in||c.thighs_in||c.calf_in||c.body_fat_pct; });
  if (histRows.length) {
    html += '<div class="section-label" style="margin-top:20px">Measurement history</div>';
    html += '<div class="card"><div class="card-body" style="overflow-x:auto;padding:0">';
    html += '<table class="hist-table"><thead><tr>';
    html += '<th>Date</th><th>Wt</th><th>Neck</th><th>Chest</th><th>Bicep</th><th>Waist</th><th>Thigh</th><th>Calf</th><th>BF%</th>';
    html += '</tr></thead><tbody>';
    histRows.forEach(function(c){
      function cell(v){ return '<td>' + (v ? fmtNum(v) : '\\u2014') + '</td>'; }
      html += '<tr>';
      html += '<td>' + fmtDateShort(c.date) + '</td>';
      html += cell(c.weight_lbs) + cell(c.neck_in) + cell(c.chest_in) + cell(c.arms_in) + cell(c.waist_in) + cell(c.thighs_in) + cell(c.calf_in) + cell(c.body_fat_pct);
      html += '</tr>';
    });
    html += '</tbody></table></div></div>';
  }
  html += '<div class="section-label" style="margin-top:20px">Log measurements</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Date</label><input type="date" id="ms-date" value="' + today() + '"></div>';
  html += '<div class="field"><label>Weight (lbs)</label><input type="number" id="ms-weight" step="0.1" inputmode="decimal" placeholder="185"></div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Neck (in)</label><input type="number" id="ms-neck" step="0.1" inputmode="decimal" placeholder="15"></div>';
  html += '<div class="field"><label>Chest (in)</label><input type="number" id="ms-chest" step="0.1" inputmode="decimal" placeholder="40"></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Bicep (in)</label><input type="number" id="ms-bicep" step="0.1" inputmode="decimal" placeholder="14"></div>';
  html += '<div class="field"><label>Waist (in)</label><input type="number" id="ms-waist" step="0.1" inputmode="decimal" placeholder="34"></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Thigh (in)</label><input type="number" id="ms-thigh" step="0.1" inputmode="decimal" placeholder="22"></div>';
  html += '<div class="field"><label>Calf (in)</label><input type="number" id="ms-calf" step="0.1" inputmode="decimal" placeholder="15"></div>';
  html += '</div>';
  html += '<div class="field"><label>Body fat (%)</label><input type="number" id="ms-bodyfat" step="0.1" inputmode="decimal" placeholder="18"></div>';
  html += '<button class="btn btn-primary" onclick="logMeasurements(' + patientId + ')">Save</button>';
  html += '<div id="ms-flash" class="flash-msg"></div>';
  html += '</div></div>';
  html += '</div>';
  return html;
}

function renderVitalsPanel(checkins, patientId) {
  const last = checkins[0];
  let html = '<div style="padding:20px">';
  if (last && (last.systolic || last.heart_rate || last.o2_sat_pct || last.blood_sugar_fasting)) {
    html += '<div class="section-label">Latest vitals</div>';
    html += '<div class="stat-grid">';
    var bpStr = (last.systolic && last.diastolic) ? (last.systolic + '/' + last.diastolic) : '\\u2014';
    html += '<div class="stat-card"><div class="stat-label">Blood pressure</div><div class="stat-value">' + bpStr + '</div></div>';
    html += '<div class="stat-card"><div class="stat-label">Heart rate</div><div class="stat-value">' + (last.heart_rate ? last.heart_rate : '\\u2014') + '<small> bpm</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">O2 sat</div><div class="stat-value">' + (last.o2_sat_pct ? fmtNum(last.o2_sat_pct) : '\\u2014') + '<small> %</small></div></div>';
    html += '<div class="stat-card"><div class="stat-label">Fasting glucose</div><div class="stat-value">' + (last.blood_sugar_fasting ? fmtNum(last.blood_sugar_fasting) : '\\u2014') + '<small> mg/dL</small></div></div>';
    html += '</div>';
  }
  var vitalsRows = checkins.filter(function(c){ return c.systolic||c.diastolic||c.heart_rate||c.o2_sat_pct||c.blood_sugar_fasting; });
  if (vitalsRows.length) {
    html += '<div class="section-label" style="margin-top:20px">Vitals history</div>';
    html += '<div class="card"><div class="card-body" style="overflow-x:auto;padding:0">';
    html += '<table class="hist-table"><thead><tr>';
    html += '<th>Date</th><th>BP</th><th>HR</th><th>O2%</th><th>Glucose</th>';
    html += '</tr></thead><tbody>';
    vitalsRows.forEach(function(c){
      function cell(v){ return '<td>' + (v ? fmtNum(v) : '\\u2014') + '</td>'; }
      var bp = (c.systolic && c.diastolic) ? (c.systolic + '/' + c.diastolic) : '\\u2014';
      html += '<tr>';
      html += '<td>' + fmtDateShort(c.date) + '</td>';
      html += '<td>' + bp + '</td>';
      html += cell(c.heart_rate) + cell(c.o2_sat_pct) + cell(c.blood_sugar_fasting);
      html += '</tr>';
    });
    html += '</tbody></table></div></div>';
  }
  html += '<div class="section-label" style="margin-top:20px">Log vitals</div>';
  html += '<div class="card"><div class="card-body">';
  html += '<div class="field"><label>Date</label><input type="date" id="v-date" value="' + today() + '"></div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Systolic</label><input type="number" id="v-systolic" step="1" inputmode="numeric" placeholder="120"></div>';
  html += '<div class="field"><label>Diastolic</label><input type="number" id="v-diastolic" step="1" inputmode="numeric" placeholder="80"></div>';
  html += '</div>';
  html += '<div class="field-row">';
  html += '<div class="field"><label>Heart rate (bpm)</label><input type="number" id="v-heartrate" step="1" inputmode="numeric" placeholder="72"></div>';
  html += '<div class="field"><label>O2 sat (%)</label><input type="number" id="v-o2sat" step="0.1" inputmode="decimal" placeholder="98"></div>';
  html += '</div>';
  html += '<div class="field"><label>Fasting glucose (mg/dL)</label><input type="number" id="v-glucose" step="1" inputmode="numeric" placeholder="90"></div>';
  html += '<button class="btn btn-primary" onclick="logVitals(' + patientId + ')">Save vitals</button>';
  html += '<div id="v-flash" class="flash-msg"></div>';
  html += '</div></div>';
  html += '</div>';
  return html;
}

'''.split('\n')

lines[start_progress:end_render_body] = new_block
c = '\n'.join(lines)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
