c = open('/home/madfella/peptidetrack/static/app.js').read()

old_header = "    html += '<th>Date</th><th>Wt</th><th>Neck</th><th>Chest</th><th>Bicep</th><th>Waist</th><th>Thigh</th><th>Calf</th><th>BF%</th>';"
new_header = "    html += '<th>Date</th><th>Wt</th><th>BF%</th><th>Neck</th><th>Chest</th><th>Bicep</th><th>Waist</th><th>Thigh</th><th>Calf</th>';"
print("header count:", c.count(old_header))
c = c.replace(old_header, new_header, 1)

old_row = "      html += cell(c.weight_lbs) + cell(c.neck_in) + cell(c.chest_in) + cell(c.arms_in) + cell(c.waist_in) + cell(c.thighs_in) + cell(c.calf_in) + cell(c.body_fat_pct);"
new_row = "      html += cell(c.weight_lbs) + cell(c.body_fat_pct) + cell(c.neck_in) + cell(c.chest_in) + cell(c.arms_in) + cell(c.waist_in) + cell(c.thighs_in) + cell(c.calf_in);"
print("row count:", c.count(old_row))
c = c.replace(old_row, new_row, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
