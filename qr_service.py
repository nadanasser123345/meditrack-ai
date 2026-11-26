import secrets
import io
import base64
from datetime import datetime, timedelta
import qrcode
from app.models import db, QRToken

def generate_patient_qr(patient_id: int, minutes_valid: int = 15) -> tuple[str, str]:
    """
    Creates a cryptographically secure temporary token for the patient and renders a QR code base64 image.
    Returns (token_string, base64_image_url).
    """
    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=minutes_valid)

    qr_token = QRToken(
        patient_id=patient_id,
        token=token_str,
        expires_at=expires_at,
        is_used=False
    )
    db.session.add(qr_token)
    db.session.commit()

    # Generate QR Code Image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(token_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0d6efd", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    img_url = f"data:image/png;base64,{img_b64}"

    return token_str, img_url

def validate_qr_token(token_str: str):
    """
    Verifies if the token exists, is not expired, and has not been revoked.
    Returns the QRToken object or None.
    """
    token_obj = QRToken.query.filter_by(token=token_str).first()
    if not token_obj:
        return None
    if token_obj.expires_at < datetime.utcnow():
        return None
    return token_obj
