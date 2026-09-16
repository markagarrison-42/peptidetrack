c = open('/home/madfella/peptidetrack/models.py').read()
old = '''    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "name":       self.name,
            "vial_size":  self.vial_size,
            "unit":       self.unit,
            "water":      self.water,
            "dose":       self.dose,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }'''
new = '''    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "name":       self.name,
            "vial_size":  self.vial_size,
            "unit":       self.unit,
            "water":      self.water,
            "dose":       self.dose,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SavedBlendCalc(db.Model):
    __tablename__ = "saved_blend_calcs"
    id              = db.Column(db.Integer, primary_key=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    water           = db.Column(db.Float, nullable=False)
    vial_unit       = db.Column(db.String(10), nullable=False)
    dose_unit       = db.Column(db.String(10), nullable=False)
    compounds_json  = db.Column(db.Text, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "name":       self.name,
            "water":      self.water,
            "vial_unit":  self.vial_unit,
            "dose_unit":  self.dose_unit,
            "compounds":  json.loads(self.compounds_json),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/models.py', 'w').write(c)
print("written")
