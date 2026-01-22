from reportlab.pdfgen import canvas
import os

def create_sample_pdf(filename, content):
    c = canvas.Canvas(filename)
    y = 800
    for line in content.split('\n'):
        c.drawString(100, y, line)
        y -= 20
    c.save()

# Sample Question Paper / Answer Key for creating test
q_content = """Q: What is the capital of France?
A: Paris
Q: Who wrote Hamlet?
A: Shakespeare
"""
create_sample_pdf("sample_questions.pdf", q_content)

# Sample Student Answer Sheet
a_content = """Q: What is the capital of France?
A: Paris
Q: Who wrote Hamlet?
A: William Shakespeare
"""
create_sample_pdf("sample_student_answers.pdf", a_content)
