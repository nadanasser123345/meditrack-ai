import csv
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.models import db, User, Patient, Doctor, Visit, QRToken
from app.services.qr_service import generate_patient_qr, validate_qr_token
from app.services.ai_service import generate_cardiac_summary, check_drug_safety, organize_patient_instructions

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    patients = Patient.query.all()
    doctor = Doctor.query.first()
    return render_template('index.html', patients=patients, doctor=doctor)

@main_bp.route('/kaggle-data')
def view_kaggle_data():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'kaggle_heart_disease_benchmark.csv')
    rows = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    return render_template('kaggle_data.html', rows=rows)

@main_bp.route('/patient/<int:patient_id>')
def patient_dashboard(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    token, qr_image_url = generate_patient_qr(patient.id)
    return render_template('patient_dashboard.html', patient=patient, qr_image_url=qr_image_url, token=token)

@main_bp.route('/doctor')
def doctor_dashboard():
    doctor = Doctor.query.first()
    return render_template('doctor_dashboard.html', doctor=doctor)

@main_bp.route('/doctor/access', methods=['POST'])
def doctor_access():
    token_str = request.form.get('token', '').strip()
    qr_token = validate_qr_token(token_str)
    if not qr_token:
        return render_template('doctor_dashboard.html', error="كود الـ QR غير صالح أو انتهت صلاحيته (المدة 15 دقيقة فقط).")
    return redirect(url_for('main.doctor_view_patient', patient_id=qr_token.patient_id))

@main_bp.route('/doctor/patient/<int:patient_id>')
def doctor_view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('clinical_view.html', patient=patient)

@main_bp.route('/api/ai/summarize/<int:patient_id>', methods=['POST'])
def api_summarize(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    summary = generate_cardiac_summary(patient.to_dict())
    return jsonify({"success": True, "summary": summary})

@main_bp.route('/api/ai/check-medication/<int:patient_id>', methods=['POST'])
def api_check_medication(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    med_name = request.json.get('medication_name', '')
    warnings = check_drug_safety(med_name, patient.to_dict())
    return jsonify({"success": True, "warnings": warnings})

@main_bp.route('/api/doctor/record-visit/<int:patient_id>', methods=['POST'])
def record_visit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.first()
    data = request.json

    diagnosis = data.get('diagnosis', '')
    complaint = data.get('complaint', '')
    findings = data.get('findings', '')
    raw_instructions = data.get('raw_instructions', '')

    # AI reorganizes instructions
    optimized = organize_patient_instructions(raw_instructions, diagnosis)

    visit = Visit(
        patient_id=patient.id,
        doctor_id=doctor.id,
        complaint=complaint,
        findings=findings,
        diagnosis=diagnosis,
        raw_instructions=raw_instructions,
        optimized_instructions=str(optimized),
        is_approved=True
    )
    db.session.add(visit)
    db.session.commit()

    return jsonify({"success": True, "visit_id": visit.id, "optimized": optimized})
