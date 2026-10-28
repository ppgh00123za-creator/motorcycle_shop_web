import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

pdfmetrics.registerFont(TTFont('SarabunTH', os.path.join(FONT_DIR, 'Sarabun-Regular.ttf'), shapable=True))
pdfmetrics.registerFont(TTFont('TahomaTH', os.path.join(FONT_DIR, 'tahoma.ttf'), shapable=True))

for font_name in ['SarabunTH', 'TahomaTH']:
    doc = SimpleDocTemplate(f'scratch/test_nee_{font_name}.pdf', pagesize=A4)
    style = ParagraphStyle(
        'TestStyle',
        fontName=font_name,
        fontSize=20,
        leading=30,
        wordWrap='LTR',
        shaping=True
    )
    # Compare "นี้" vs "ที่" vs "ชี้" vs "หนี้"
    story = [
        Paragraph(f"คำทดสอบ {font_name}:", style),
        Paragraph("นี้ ที่ ชี้ หนี้ ปิ๊ง ผู้ ซื้อ สิทธิ์", style),
        Paragraph("เอกสารนี้ไว้", style)
    ]
    doc.build(story)
    
    doc_fitz = fitz.open(f'scratch/test_nee_{font_name}.pdf')
    pix = doc_fitz[0].get_pixmap(dpi=150)
    pix.save(f'scratch/test_nee_{font_name}.png')

print("Generated test_nee PNGs")
