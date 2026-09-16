c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  el.innerHTML =
    safetyBanner() +
    '<div class="section">' +
    '<div class="section-label">Reconstitution calculator</div>' +'''
new = '''  el.innerHTML =
    safetyBanner() +
    '<div class="inner-tabs">' +
    '<button class="inner-tab active" onclick="switchCalcTab(\\'single\\', this)">Single</button>' +
    '<button class="inner-tab" onclick="switchCalcTab(\\'blend\\', this)">Blend</button>' +
    '</div>' +
    '<div class="inner-panel active" id="calc-single">' +
    '<div class="section">' +
    '<div class="section-label">Reconstitution calculator</div>' +'''
n = c.count(old)
print("count:", n)
if n == 1:
    c = c.replace(old, new, 1)
    open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
    print("written")
else:
    print("ABORTED")
