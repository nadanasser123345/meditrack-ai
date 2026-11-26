from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_type = db.Column(db.String(5), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    # Cardiac Medical Record Details
    chronic_conditions = db.Column(db.Text, nullable=True)
    surgical_history = db.Column(db.Text, nullable=True)
    ejection_fraction = db.Column(db.String(10), nullable=True)  # e.g., "48%"
    lifestyle_notes = db.Column(db.Text, nullable=True)
    last_ecg_summary = db.Column(db.Text, nullable=True)

    # Relationships
    medications = db.relationship('Medication', backref='patient', lazy=True, cascade="all, delete-orphan")
    allergies = db.relationship('Allergy', backref='patient', lazy=True, cascade="all, delete-orphan")
    visits = db.relationship('Visit', backref='patient', lazy=True, cascade="all, delete-orphan")
    qr_tokens = db.relationship('QRToken', backref='patient', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.user.full_name,
            "age": self.age,
            "gender": self.gender,
            "blood_type": self.blood_type,
            "phone": self.phone,
            "cardiac_history": {
                "chronic_conditions": self.chronic_conditions,
                "surgical_history": self.surgical_history,
                "ejection_fraction": self.ejection_fraction,
                "lifestyle": self.lifestyle_notes,
                "last_ecg_summary": self.last_ecg_summary
            },
            "current_medications": [m.to_dict() for m in self.medications if m.is_current],
            "allergies": [a.to_dict() for a in self.allergies],
            "past_visits": [v.to_dict() for v in self.visits]
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    specialty = db.Column(db.String(100), default='Cardiology & Cardiovascular (أمراض القلب والأوعية الدموية)')
    clinic_address = db.Column(db.String(200), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)

    visits = db.relationship('Visit', backref='doctor', lazy=True)

class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(50), nullable=True)
    frequency = db.Column(db.String(100), nullable=True)
    purpose = db.Column(db.String(200), nullable=True)
    is_current = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "name": self.name,
            "dose": self.dosage,
            "frequency": self.frequency,
            "purpose": self.purpose
        }

class Allergy(db.Model):
    __tablename__ = 'allergies'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    allergen = db.Column(db.String(150), nullable=False)
    severity = db.Column(db.String(50), nullable=True)  # Mild, Moderate, Severe
    reaction = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "allergen": self.allergen,
            "severity": self.severity,
            "reaction": self.reaction
        }

class Visit(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    complaint = db.Column(db.Text, nullable=True)
    findings = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    raw_instructions = db.Column(db.Text, nullable=True)
    optimized_instructions = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "date": self.visit_date.strftime("%Y-%m-%d"),
            "doctor": self.doctor.user.full_name if self.doctor and self.doctor.user else "طبيب قلب",
            "complaint": self.complaint,
            "findings": self.findings,
            "diagnosis": self.diagnosis,
            "optimized_instructions": self.optimized_instructions,
            "is_approved": self.is_approved
        }

class QRToken(db.Model):
    __tablename__ = 'qr_tokens'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
