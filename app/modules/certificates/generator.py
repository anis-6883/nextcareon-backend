"""app/modules/certificates/generator.py - PDF certificate generation."""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from app.core.config import settings


def generate_certificate(
    student_name: str,
    course_title: str,
    completion_date: str,
) -> bytes:
    """Generate a PDF certificate for course completion."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add certificate content
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 2 * inch, "Certificate of Completion")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 3 * inch, f"This certifies that")
    c.drawCentredString(width / 2, height - 3.5 * inch, f"{student_name}")
    c.drawCentredString(width / 2, height - 4 * inch, f"has completed")
    c.drawCentredString(width / 2, height - 4.5 * inch, f"{course_title}")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 5.5 * inch, f"Date: {completion_date}")
    c.drawCentredString(
        width / 2, height - 6 * inch, f"Issued by: {settings.CERTIFICATE_ISSUER_NAME}"
    )
    
    # Add signature line
    c.line(width / 2 - 1.5 * inch, 2 * inch, width / 2 + 1.5 * inch, 2 * inch)
    c.drawCentredString(
        width / 2, 1.5 * inch, f"{settings.CERTIFICATE_SIGNATURE_NAME}"
    )
    
    c.save()
    buffer.seek(0)
    return buffer.read()
