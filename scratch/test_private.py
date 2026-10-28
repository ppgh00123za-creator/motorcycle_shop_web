import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uharfbuzz

f = TTFont('TahomaTH', 'static/fonts/tahoma.ttf')
_ = f.hbFace
f._TTFont__hbPrivate = 0x0080
pdfmetrics.registerFont(f)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz

doc = SimpleDocTemplate('scratch/test_private_sub0.pdf', pagesize=A4)
style = ParagraphStyle(
    'TestStyle',
    fontName='TahomaTH',
    fontSize=18,
    leading=28,
    wordWrap='LTR',
    shaping=True
)

test_sentence = "• โปรดเก็บเอกสารนี้ไว้เป็นหลักฐานประกอบการรับประกันและจดทะเบียนรถ ที่อยู่ ผู้ซื้อ ชำระเงินแล้ว"
story = [Paragraph(test_sentence, style)]
doc.build(story)

doc_fitz = fitz.open('scratch/test_private_sub0.pdf')
pix = doc_fitz[0].get_pixmap(dpi=150)
pix.save('scratch/test_private_sub0.png')
print("Successfully generated scratch/test_private_sub0.png")
