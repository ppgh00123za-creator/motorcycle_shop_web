import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Sarabun', 'static/fonts/Sarabun-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))

doc = SimpleDocTemplate('scratch/test_thai_shaped.pdf', pagesize=A4)

# Test words with stacked vowels & tones:
# ที่อยู่, ผู้ซื้อ, ศูนย์, ซิ่ง, ชำระเงินแล้ว, พื้นที่, ปิ๊ง, เก้าอี้
text = "ทดสอบ: ที่อยู่ ผู้ซื้อ ศูนย์บริการ สายซิ่ง ชำระเงินแล้ว ป้ายทะเบียน พื้นที่ น้ำมัน ติดตั้ง สิทธิ์"

style_normal = ParagraphStyle(
    'Normal',
    fontName='Sarabun',
    fontSize=14,
    leading=22,
)

style_shaped = ParagraphStyle(
    'Shaped',
    fontName='Sarabun',
    fontSize=14,
    leading=22,
    wordWrap='LTR',
    shaping=True
)

style_tahoma = ParagraphStyle(
    'TahomaNormal',
    fontName='Tahoma',
    fontSize=14,
    leading=22,
)

style_tahoma_shaped = ParagraphStyle(
    'TahomaShaped',
    fontName='Tahoma',
    fontSize=14,
    leading=22,
    wordWrap='LTR',
    shaping=True
)

story = [
    Paragraph(f"<b>Sarabun (Default):</b> {text}", style_normal),
    Spacer(1, 15),
    Paragraph(f"<b>Sarabun (Shaped LTR):</b> {text}", style_shaped),
    Spacer(1, 15),
    Paragraph(f"<b>Tahoma (Default):</b> {text}", style_tahoma),
    Spacer(1, 15),
    Paragraph(f"<b>Tahoma (Shaped LTR):</b> {text}", style_tahoma_shaped),
]

try:
    doc.build(story)
    print("Successfully built scratch/test_thai_shaped.pdf")
except Exception as e:
    import traceback
    traceback.print_exc()
