c = open('/home/madfella/peptidetrack/static/app.js').read()

old1 = "let BLEND_EDITING_ID = null;"
new1 = "let BLEND_EDITING_ID = null;\nlet BLEND_LOADED = null;"
n1 = c.count(old1)
print("global count:", n1)
assert n1 == 1
c = c.replace(old1, new1, 1)

old2 = '''    BLEND_EDITING_ID = blendId;
    BLEND_ROW_IDS = blend.compounds.map(function(_, i) { return i + 1; });'''
new2 = '''    BLEND_EDITING_ID = blendId;
    BLEND_LOADED = {
      name: blend.name,
      water: blend.water,
      vialUnit: blend.vial_unit,
      doseUnit: blend.dose_unit,
      compounds: blend.compounds.map(function(c) { return { name: c.name, amount: c.amount }; }),
    };
    BLEND_ROW_IDS = blend.compounds.map(function(_, i) { return i + 1; });'''
n2 = c.count(old2)
print("snapshot count:", n2)
assert n2 == 1
c = c.replace(old2, new2, 1)

open('/home/madfella/peptidetrack/static/app.js', 'w').write(c)
print("written")
