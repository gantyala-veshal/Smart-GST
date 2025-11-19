from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import time

def generate_invoice(text):
    name = f"invoice_{int(time.time())}.pdf"
    c = canvas.Canvas(name, pagesize=A4)
    c.setFont("Helvetica", 12)
    y = 800
    for line in text.split("\n"):
        c.drawString(40, y, line)
        y -= 18
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    c.save()
    return name
