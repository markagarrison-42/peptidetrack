c = open('/home/madfella/peptidetrack/models.py').read()
old = '''    dose       = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "name":       self.name,
            "vial_size":  self.vial_size,
            "unit":       self.unit,
            "water":      self.water,
            "dose":       self.dose,
            "created_at": self.created_at.isoformat() if self.created_at else None,'''
new = '''    dose       = db.Column(db.Float, nullable=False)
    dose_unit  = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "name":       self.name,
            "vial_size":  self.vial_size,
            "unit":       self.unit,
            "water":      self.water,
            "dose":       self.dose,
            "dose_unit":  self.dose_unit or self.unit,
            "created_at": self.created_at.isoformat() if self.created_at else None,'''
n = c.count(old)
print("count:", n)
assert n == 1, "aborting"
c = c.replace(old, new, 1)
open('/home/madfella/peptidetrack/models.py', 'w').write(c)
print("written")
