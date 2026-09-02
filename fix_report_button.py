c = open('/home/madfella/peptidetrack/static/app.js').read()
old = '''  html += '<button class="btn btn-ghost" style="margin:0 20px 12px" onclick="showReport()">Print / Save Report</button>';'''
new = '''  html += '<div style="padding:20px 20px 0"><button class="btn btn-ghost" style="width:100%" onclick="showReport()">Print / Save Report</button></div>';'''
print("count:", c.count(old))
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
