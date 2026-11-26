import json
import os
from flask import Flask
from app.models import db, User, Patient, Doctor, Medication, Allergy, Visit

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure SQLite Database
    db_path = os.path.join(app.root_path, 'meditrack.db')
    app.config.from_mapping(
        SECRET_KEY='meditrack-ai-secret-key-for-development',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_cardiology_data()

    # Register Blueprints / Routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

def seed_cardiology_data():
    """Seeds the 5 realistic cardiology cases if database is empty."""
    if Patient.query.first():
        return  # Already seeded

    # Create Doctor account
    doc_user = User(
        username="dr_hazem",
        password_hash="pbkdf2:sha256:cardio123",
        role="doctor",
        full_name="د. حازم النجار (استشاري القلب والأوعية الدموية)"
    )
    db.session.add(doc_user)
    db.session.flush()

    doctor = Doctor(
        user_id=doc_user.id,
        specialty="أمراض القلب وقسطرة الشرايين التاجية (Cardiology)",
        clinic_address="عيادة النجار التخصصية - المهندسين، الجيزة",
        license_number="EGY-MED-44892"
    )
    db.session.add(doctor)

    # Load 5 patient JSON profiles
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cardiology_patients.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            patients_data = json.load(f)

        for p_data in patients_data:
            user = User(
                username=f"patient_{p_data['id']}",
                password_hash="pbkdf2:sha256:patient123",
                role="patient",
                full_name=p_data['full_name']
            )
            db.session.add(user)
            db.session.flush()

            c_hist = p_data['cardiac_history']
            patient = Patient(
                user_id=user.id,
                age=p_data['age'],
                gender=p_data['gender'],
                blood_type=p_data['blood_type'],
                phone=p_data['phone'],
                chronic_conditions=c_hist['chronic_conditions'],
                surgical_history=c_hist['surgical_history'],
                ejection_fraction=c_hist['ejection_fraction'],
                lifestyle_notes=c_hist['lifestyle'],
                last_ecg_summary=c_hist['last_ecg_summary']
            )
            db.session.add(patient)
            db.session.flush()

            # Add Medications
            for m in p_data.get('current_medications', []):
                med = Medication(
                    patient_id=patient.id,
                    name=m['name'],
                    dosage=m['dose'],
                    frequency=m['frequency'],
                    purpose=m['purpose'],
                    is_current=True
                )
                db.session.add(med)

            # Add Allergies
            for a in p_data.get('allergies', []):
                alg = Allergy(
                    patient_id=patient.id,
                    allergen=a['allergen'],
                    severity=a['severity'],
                    reaction=a['reaction']
                )
                db.session.add(alg)

            # Add Past Visits
            for v in p_data.get('past_visits', []):
                visit = Visit(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    complaint=v['complaint'],
                    findings=v['findings'],
                    diagnosis="متابعة دورية للشرايين التاجية",
                    raw_instructions=v['action'],
                    optimized_instructions="تم تعديل الجرعات والتشديد على المتابعة الدورية للوزن وضغط الدم.",
                    is_approved=True
                )
                db.session.add(visit)

        db.session.commit()
        print("[MediTrack AI] Successfully seeded 5 rich cardiology patients and doctor profile.")
