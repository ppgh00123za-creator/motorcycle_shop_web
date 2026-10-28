import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Sarabun', 'static/fonts/Sarabun-Regular.ttf'))
if os.path.exists('C:/Windows/Fonts/tahoma.ttf'):
    pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))

doc = SimpleDocTemplate('scratch/test_thai.pdf', pagesize=A4)
test_text = "ทดสอบภาษาไทย: ที่อยู่ ผู้ดูแลระบบ ศูนย์จำหน่าย ชำระเงินแล้ว ป้ายทะเบียน น้ำมัน ติดตั้ง สิทธิ์ พรบ."

story = [
    Paragraph(f"<b>Sarabun:</b> {test_text}", ParagraphStyle('SarabunStyle', fontName='Sarabun', fontSize=14, leading=22)),
    Spacer(1, 20),
]
if 'Tahoma' in pdfmetrics.getRegisteredFontNames():
    story.append(Paragraph(f"<b>Tahoma:</b> {test_text}", ParagraphStyle('TahomaStyle', fontName='Tahoma', fontSize=14, leading=22)))

doc.build(story)
print("PDF created at scratch/test_thai.pdf")
