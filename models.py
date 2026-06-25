from extensions import db
from flask_login import UserMixin
from datetime import datetime
# ── Users ──────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20),  default="patient")   # practitioner | patient
    practitioner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    # Patient profile
    first_name    = db.Column(db.String(80),  nullable=True)
    last_name     = db.Column(db.String(80),  nullable=True)
    date_of_birth = db.Column(db.Date,        nullable=True)
    weight_lbs    = db.Column(db.Float,       nullable=True)
    height_in     = db.Column(db.Float,       nullable=True)
    sex           = db.Column(db.String(10),   nullable=True)
    goals         = db.Column(db.Text,        nullable=True)
    notes         = db.Column(db.Text,        nullable=True)
    active        = db.Column(db.Boolean,     default=True)
    invite_code   = db.Column(db.String(20),  unique=True, nullable=True)
    onboarding_complete = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    # Relationships
    protocols  = db.relationship("Protocol",  backref="patient",       lazy=True, foreign_keys="Protocol.patient_id",       cascade="all, delete-orphan")
    checkins   = db.relationship("CheckIn",   backref="patient",       lazy=True, foreign_keys="CheckIn.patient_id",        cascade="all, delete-orphan")
    dose_logs  = db.relationship("DoseLog",   backref="patient",       lazy=True, foreign_keys="DoseLog.patient_id",        cascade="all, delete-orphan")
    labs       = db.relationship("Lab",       backref="patient",       lazy=True, foreign_keys="Lab.patient_id",            cascade="all, delete-orphan")
    photos     = db.relationship("Photo",     backref="patient",       lazy=True, foreign_keys="Photo.patient_id",          cascade="all, delete-orphan")
    patients   = db.relationship("User",      backref=db.backref("practitioner", remote_side=[id]), lazy=True, foreign_keys=[practitioner_id])

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.today().date()
            dob   = self.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    def to_dict(self):
        return {
            "id":           self.id,
            "username":     self.username,
            "email":        self.email,
            "role":         self.role,
            "first_name":   self.first_name,
            "last_name":    self.last_name,
            "full_name":    self.full_name,
            "age":          self.age,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "weight_lbs":   self.weight_lbs,
            "height_in":    self.height_in,
            "sex":          self.sex,
            "goals":        self.goals,
            "notes":        self.notes,
            "active":       self.active,
            "onboarding_complete": self.onboarding_complete,
            "created_at":   self.created_at.isoformat(),
        }


class InviteCode(db.Model):
    __tablename__    = "invite_codes"
    id               = db.Column(db.Integer, primary_key=True)
    code             = db.Column(db.String(20), unique=True, nullable=False)
    practitioner_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    used             = db.Column(db.Boolean, default=False)
    used_by_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at       = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id":   self.id,
            "code": self.code,
            "used": self.used,
            "created_at": self.created_at.isoformat(),
        }


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token      = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        return not self.used and self.expires_at > datetime.utcnow()


# ── Protocol Item History ──────────────────────────────
class ProtocolItemHistory(db.Model):
    __tablename__    = "protocol_item_history"
    id               = db.Column(db.Integer, primary_key=True)
    protocol_item_id = db.Column(db.Integer, db.ForeignKey("protocol_items.id"), nullable=False)
    changed_by_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    changed_at       = db.Column(db.DateTime, default=datetime.utcnow)
    field_changed    = db.Column(db.String(50),  nullable=False)
    old_value        = db.Column(db.String(100), nullable=True)
    new_value        = db.Column(db.String(100), nullable=True)
    notes            = db.Column(db.String(200), nullable=True)

    protocol_item = db.relationship("ProtocolItem", backref="history", lazy=True)

    def to_dict(self):
        return {
            "id":               self.id,
            "protocol_item_id": self.protocol_item_id,
            "changed_at":       self.changed_at.isoformat(),
            "field_changed":    self.field_changed,
            "old_value":        self.old_value,
            "new_value":        self.new_value,
            "notes":            self.notes,
        }


# ── Compounds ──────────────────────────────────────────
class Compound(db.Model):
    __tablename__ = "compounds"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), unique=True, nullable=False)
    category      = db.Column(db.String(50),  nullable=False)
    default_route = db.Column(db.String(50),  nullable=True)
    typical_dose_min = db.Column(db.Float,    nullable=True)
    typical_dose_max = db.Column(db.Float,    nullable=True)
    dose_unit     = db.Column(db.String(20),  default="mg")
    frequency     = db.Column(db.String(50),  nullable=True)
    has_titration = db.Column(db.Boolean,     default=False)
    titration_notes = db.Column(db.Text,      nullable=True)
    notes         = db.Column(db.Text,        nullable=True)
    active        = db.Column(db.Boolean,     default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":               self.id,
            "name":             self.name,
            "category":         self.category,
            "default_route":    self.default_route,
            "typical_dose_min": self.typical_dose_min,
            "typical_dose_max": self.typical_dose_max,
            "dose_unit":        self.dose_unit,
            "frequency":        self.frequency,
            "has_titration":    self.has_titration,
            "titration_notes":  self.titration_notes,
            "notes":            self.notes,
            "active":           self.active,
        }


# ── Protocols ──────────────────────────────────────────
class Protocol(db.Model):
    __tablename__    = "protocols"
    id               = db.Column(db.Integer, primary_key=True)
    patient_id       = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    practitioner_id  = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    name             = db.Column(db.String(100), nullable=False)
    phase            = db.Column(db.String(50),  default="Loading")
    start_date       = db.Column(db.Date,        nullable=True)
    review_date      = db.Column(db.Date,        nullable=True)
    notes            = db.Column(db.Text,        nullable=True)
    active           = db.Column(db.Boolean,     default=True)
    created_at       = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("ProtocolItem", backref="protocol", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":              self.id,
            "patient_id":      self.patient_id,
            "practitioner_id": self.practitioner_id,
            "name":            self.name,
            "phase":           self.phase,
            "start_date":      self.start_date.isoformat() if self.start_date else None,
            "review_date":     self.review_date.isoformat() if self.review_date else None,
            "notes":           self.notes,
            "active":          self.active,
            "items":           [i.to_dict() for i in self.items],
        }


class ProtocolItem(db.Model):
    __tablename__  = "protocol_items"
    id             = db.Column(db.Integer, primary_key=True)
    protocol_id    = db.Column(db.Integer, db.ForeignKey("protocols.id"), nullable=False)
    compound_id    = db.Column(db.Integer, db.ForeignKey("compounds.id"), nullable=False)
    dose_mg        = db.Column(db.Float,   nullable=False)
    frequency      = db.Column(db.String(50),  nullable=False)
    route          = db.Column(db.String(50),  nullable=True)
    timing         = db.Column(db.String(100), nullable=True)
    phase          = db.Column(db.String(50),  nullable=True)
    vial_size_mg   = db.Column(db.Float, nullable=True)
    recon_volume_ml = db.Column(db.Float, nullable=True)
    notes          = db.Column(db.Text,  nullable=True)
    active         = db.Column(db.Boolean, default=True)
    dose_overridden = db.Column(db.Boolean, default=False)
    reminder_time  = db.Column(db.String(5), nullable=True)

    compound = db.relationship("Compound", backref="protocol_items", lazy=True)

    @property
    def concentration_mg_per_ml(self):
        if self.vial_size_mg and self.recon_volume_ml:
            return round(self.vial_size_mg / self.recon_volume_ml, 4)
        return None

    @property
    def dose_ml(self):
        conc = self.concentration_mg_per_ml
        if conc and conc > 0:
            return round(self.dose_mg / conc, 3)
        return None

    @property
    def dose_units(self):
        ml = self.dose_ml
        if ml is not None:
            return round(ml * 100, 1)
        return None

    def to_dict(self):
        return {
            "id":                    self.id,
            "protocol_id":           self.protocol_id,
            "compound_id":           self.compound_id,
            "compound_name":         self.compound.name if self.compound else None,
            "compound_category":     self.compound.category if self.compound else None,
            "dose_mg":               self.dose_mg,
            "frequency":             self.frequency,
            "route":                 self.route,
            "timing":                self.timing,
            "phase":                 self.phase,
            "vial_size_mg":          self.vial_size_mg,
            "recon_volume_ml":       self.recon_volume_ml,
            "concentration_mg_per_ml": self.concentration_mg_per_ml,
            "dose_ml":               self.dose_ml,
            "dose_units":            self.dose_units,
            "notes":                 self.notes,
            "active":                self.active,
            "dose_overridden":       self.dose_overridden,
            "reminder_time":         self.reminder_time,
        }


# ── Dose Logs ──────────────────────────────────────────
class DoseLog(db.Model):
    __tablename__      = "dose_logs"
    id                 = db.Column(db.Integer, primary_key=True)
    patient_id         = db.Column(db.Integer, db.ForeignKey("users.id"),         nullable=False)
    protocol_item_id   = db.Column(db.Integer, db.ForeignKey("protocol_items.id"), nullable=False)
    date               = db.Column(db.Date,    nullable=False)
    time               = db.Column(db.String(10), nullable=True)
    dose_mg_taken      = db.Column(db.Float,   nullable=True)
    injection_site     = db.Column(db.String(50), nullable=True)
    notes              = db.Column(db.Text,    nullable=True)
    off_schedule       = db.Column(db.Boolean, default=False)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    protocol_item = db.relationship("ProtocolItem", backref="dose_logs", lazy=True)

    def to_dict(self):
        return {
            "id":               self.id,
            "patient_id":       self.patient_id,
            "protocol_item_id": self.protocol_item_id,
            "compound_name":    self.protocol_item.compound.name if self.protocol_item and self.protocol_item.compound else None,
            "date":             self.date.isoformat(),
            "time":             self.time,
            "dose_mg_taken":    self.dose_mg_taken,
            "injection_site":   self.injection_site,
            "notes":            self.notes,
            "off_schedule":     self.off_schedule or False,
        }


# ── Check-ins ──────────────────────────────────────────
SIDE_EFFECTS = [
    "Nausea", "Fatigue", "Headache", "Injection site reaction",
    "Dizziness", "Flushing", "Insomnia", "Increased appetite",
    "Decreased appetite", "Mood changes", "Water retention",
    "Joint pain", "Muscle aches", "Brain fog", "Other"
]

class CheckIn(db.Model):
    __tablename__    = "checkins"
    id               = db.Column(db.Integer, primary_key=True)
    patient_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date             = db.Column(db.Date,    nullable=False)
    weight_lbs       = db.Column(db.Float,   nullable=True)
    energy           = db.Column(db.Integer, nullable=True)
    mood             = db.Column(db.Integer, nullable=True)
    sleep_quality    = db.Column(db.Integer, nullable=True)
    libido           = db.Column(db.Integer, nullable=True)
    appetite         = db.Column(db.Integer, nullable=True)
    overall          = db.Column(db.Integer, nullable=True)
    side_effects     = db.Column(db.Text,    nullable=True)
    notes            = db.Column(db.Text,    nullable=True)
    waist_in         = db.Column(db.Float,   nullable=True)
    hips_in          = db.Column(db.Float,   nullable=True)
    chest_in         = db.Column(db.Float,   nullable=True)
    arms_in          = db.Column(db.Float,   nullable=True)
    thighs_in        = db.Column(db.Float,   nullable=True)
    neck_in          = db.Column(db.Float,   nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":           self.id,
            "patient_id":   self.patient_id,
            "date":         self.date.isoformat(),
            "weight_lbs":   self.weight_lbs,
            "energy":       self.energy,
            "mood":         self.mood,
            "sleep_quality": self.sleep_quality,
            "libido":       self.libido,
            "appetite":     self.appetite,
            "overall":      self.overall,
            "side_effects": self.side_effects.split(",") if self.side_effects else [],
            "notes":        self.notes,
            "waist_in":     self.waist_in,
            "hips_in":      self.hips_in,
            "chest_in":     self.chest_in,
            "arms_in":      self.arms_in,
            "thighs_in":    self.thighs_in,
            "neck_in":      self.neck_in,
        }


# ── Labs ───────────────────────────────────────────────
class Lab(db.Model):
    __tablename__  = "labs"
    id             = db.Column(db.Integer, primary_key=True)
    patient_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date           = db.Column(db.Date,    nullable=False)
    test_name      = db.Column(db.String(100), nullable=False)
    value          = db.Column(db.Float,   nullable=False)
    unit           = db.Column(db.String(30),  nullable=True)
    ref_range_low  = db.Column(db.Float,   nullable=True)
    ref_range_high = db.Column(db.Float,   nullable=True)
    notes          = db.Column(db.Text,    nullable=True)
    entered_by_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def in_range(self):
        if self.ref_range_low is not None and self.ref_range_high is not None:
            return self.ref_range_low <= self.value <= self.ref_range_high
        return None

    def to_dict(self):
        return {
            "id":            self.id,
            "patient_id":    self.patient_id,
            "date":          self.date.isoformat(),
            "test_name":     self.test_name,
            "value":         self.value,
            "unit":          self.unit,
            "ref_range_low": self.ref_range_low,
            "ref_range_high":self.ref_range_high,
            "in_range":      self.in_range,
            "notes":         self.notes,
        }


# ── Lab Attachments ────────────────────────────────────
class LabAttachment(db.Model):
    __tablename__   = "lab_attachments"
    id              = db.Column(db.Integer, primary_key=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date            = db.Column(db.Date,    nullable=False)
    cloudinary_id   = db.Column(db.String(200), nullable=False)
    cloudinary_url  = db.Column(db.String(500), nullable=False)
    file_type       = db.Column(db.String(20),  nullable=True)
    notes           = db.Column(db.String(200), nullable=True)
    created_at      = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "patient_id":    self.patient_id,
            "date":          self.date.isoformat(),
            "cloudinary_url": self.cloudinary_url,
            "file_type":     self.file_type,
            "notes":         self.notes,
        }


# ── Photos ─────────────────────────────────────────────
class Photo(db.Model):
    __tablename__   = "photos"
    id              = db.Column(db.Integer, primary_key=True)
    patient_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date            = db.Column(db.Date,    nullable=False)
    cloudinary_id   = db.Column(db.String(200), nullable=False)
    cloudinary_url  = db.Column(db.String(500), nullable=False)
    angle           = db.Column(db.String(30),  nullable=True)
    notes           = db.Column(db.Text,        nullable=True)
    shared_with_practitioner = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "patient_id":    self.patient_id,
            "date":          self.date.isoformat(),
            "cloudinary_url": self.cloudinary_url,
            "angle":         self.angle,
            "notes":         self.notes,
            "shared_with_practitioner": self.shared_with_practitioner,
        }


# ── Titration Templates ────────────────────────────────
class TitrationTemplate(db.Model):
    __tablename__ = "titration_templates"
    id            = db.Column(db.Integer, primary_key=True)
    compound_id   = db.Column(db.Integer, db.ForeignKey("compounds.id"), nullable=False)
    week_number   = db.Column(db.Integer, nullable=False)
    dose_mg       = db.Column(db.Float,   nullable=False)
    notes         = db.Column(db.String(200), nullable=True)

    compound = db.relationship("Compound", backref="titration_steps", lazy=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "compound_id": self.compound_id,
            "week_number": self.week_number,
            "dose_mg":     self.dose_mg,
            "notes":       self.notes,
        }


# ── Patient Weight Log ─────────────────────────────────
class WeightLog(db.Model):
    __tablename__ = "weight_logs"
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date       = db.Column(db.Date,    nullable=False)
    weight_lbs = db.Column(db.Float,   nullable=False)
    notes      = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "date":       self.date.isoformat(),
            "weight_lbs": self.weight_lbs,
            "notes":      self.notes,
        }


# ── Patient Diary ──────────────────────────────────────
class DiaryEntry(db.Model):
    __tablename__ = "diary_entries"
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date       = db.Column(db.Date,    nullable=False)
    body       = db.Column(db.Text,    nullable=False)
    mood_tag   = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "patient_id": self.patient_id,
            "date":       self.date.isoformat(),
            "body":       self.body,
            "mood_tag":   self.mood_tag,
            "created_at": self.created_at.isoformat(),
        }


# ── Push Subscriptions ─────────────────────────────────
class PushSubscription(db.Model):
    __tablename__ = "push_subscriptions"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    endpoint   = db.Column(db.Text,    nullable=False)
    p256dh     = db.Column(db.Text,    nullable=False)
    auth       = db.Column(db.Text,    nullable=False)
    user_agent = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":       self.id,
            "user_id":  self.user_id,
            "endpoint": self.endpoint,
        }
