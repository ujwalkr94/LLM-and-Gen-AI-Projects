from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas 
from io import BytesIO

def generate_pdf(explanations):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x, y = 40, height - 50

    for item in explanations:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, f"File: {item['path']}")
        y -= 20

        c.setFont("Helvetica", 10)
        for line in item["text"].splitlines():
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(x, y, line[:90])  # Trim long lines
            y -= 14

        y -= 30  # Gap between files

    c.save()
    buffer.seek(0)
    return buffer
