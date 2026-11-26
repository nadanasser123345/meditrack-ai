import os
import json
from app import create_app
from app.models import db, User, Patient, Doctor, Medication, Allergy, Visit, QRToken

app = create_app()

with app.app_context():
    # Remove old database file to have a fresh 10-patient database
    db.drop_all()
    db.create_all()

    # Re-create Doctor
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

    # Load 10 patients
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'cardiology_patients.json')
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
                name=m.get('name', 'دواء'),
                dosage=m.get('dose', ''),
                frequency=m.get('frequency', 'يومياً'),
                purpose=m.get('purpose', ''),
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
                diagnosis="متابعة سريرية لحالة القلب وتنسيق العلاج",
                raw_instructions=v['action'],
                optimized_instructions="الالتزام بمواعيد الدواء ومراقبة أي أعراض غير معتادة.",
                is_approved=True
            )
            db.session.add(visit)

    db.session.commit()
    print(f"SUCCESS: Seeded {len(patients_data)} full cardiology patients successfully!")
