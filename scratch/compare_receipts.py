import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

pdfmetrics.registerFont(TTFont('SarabunTH', os.path.join(FONT_DIR, 'Sarabun-Regular.ttf'), shapable=True))
pdfmetrics.registerFont(TTFont('SarabunTH-Bold', os.path.join(FONT_DIR, 'Sarabun-Bold.ttf'), shapable=True))
pdfmetrics.registerFont(TTFont('TahomaTH', os.path.join(FONT_DIR, 'tahoma.ttf'), shapable=True))
pdfmetrics.registerFont(TTFont('TahomaTH-Bold', os.path.join(FONT_DIR, 'tahomabd.ttf'), shapable=True))

def build_test_pdf(font_regular, font_bold, filename):
    style_shop_info = ParagraphStyle(
        name=f'ShopInfo_{font_regular}',
        fontName=font_regular,
        fontSize=11,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#222222')
    )
    style_receipt_meta = ParagraphStyle(
        name=f'ReceiptMeta_{font_regular}',
        fontName=font_regular,
        fontSize=11,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        alignment=2,
        textColor=colors.HexColor('#222222')
    )
    style_cell = ParagraphStyle(
        name=f'CellText_{font_regular}',
        fontName=font_regular,
        fontSize=10.5,
        leading=15,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#222222')
    )
    style_cell_bold = ParagraphStyle(
        name=f'CellTextBold_{font_bold}',
        fontName=font_bold,
        fontSize=10.5,
        leading=15,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#111111')
    )
    style_cell_right_bold = ParagraphStyle(
        name=f'CellTextRightBold_{font_bold}',
        fontName=font_bold,
        fontSize=11,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        alignment=2,
        textColor=colors.HexColor('#cc0000')
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )
    story = []

    header_data = [
        [
            Paragraph(
                f"<b>160 ธีระ สายซิ่ง (160 Teera Sai Sing) - [{font_regular}]</b><br/>"
                "ศูนย์จำหน่ายรถจักรยานยนต์มาตรฐาน (ขนาดไม่เกิน 160 cc)<br/>"
                "899/22 หมู่บ้านศรีมงคล ต.ศิลา อ.เมืองขอนแก่น จ.ขอนแก่น 40000<br/>"
                "โทร: 065-718-2338 | Facebook: Teera Jantharasorn<br/>"
                "เวลาทำการ: วันพุธ 09:00 - 18:00 น.",
                style_shop_info
            ),
            Paragraph(
                "<b>ใบเสร็จรับเงิน / ใบส่งมอบสินค้า</b><br/>"
                "<b>เลขที่เอกสาร:</b> REC-20261027-0001<br/>"
                "<b>เลขที่คำสั่งซื้อ:</b> ORD-20261027-0001<br/>"
                "<b>วันที่ออกเอกสาร:</b> 2026-10-26 17:42:36",
                style_receipt_meta
            )
        ]
    ]
    header_table = Table(header_data, colWidths=[10 * cm, 8 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cc0000'), spaceBefore=2, spaceAfter=8))

    cust_info = [
        [
            Paragraph(
                "<b>ข้อมูลลูกค้าผู้ซื้อ:</b><br/>"
                "<b>ชื่อ-นามสกุล:</b> ผู้ดูแลระบบ (Admin)<br/>"
                "<b>เบอร์โทรศัพท์:</b> 081-999-8888<br/>"
                "<b>วิธีรับสินค้า:</b> รับรถที่ร้าน (ศูนย์ขอนแก่น)<br/>"
                "<b>ที่อยู่:</b> สำนักงานใหญ่<br/>"
                "<b>หมายเหตุจัดส่ง:</b> ทดลองซื้อ",
                style_cell
            ),
            Paragraph(
                "<b>ข้อมูลการชำระเงิน:</b><br/>"
                "<b>สถานะการชำระ:</b> <font color='#059669'><b>[ผ่าน] ชำระเงินแล้ว (ยืนยันเมื่อ 2026-10-26 17:56:28)</b></font><br/>"
                "<b>วิธีชำระเงิน:</b> โอนเงินผ่านธนาคารพร้อมหลักฐานสลิป<br/>"
                "<b>สถานะคำสั่งซื้อ:</b> ชำระเงินแล้ว",
                style_cell
            )
        ]
    ]
    cust_table = Table(cust_info, colWidths=[10 * cm, 8 * cm])
    cust_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e5e5')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 0.4 * cm))

    # Items table
    table_data = [
        [
            Paragraph("<b>ลำดับ</b>", style_cell_bold),
            Paragraph("<b>รหัสสินค้า</b>", style_cell_bold),
            Paragraph("<b>รายการรุ่นรถจักรยานยนต์</b>", style_cell_bold),
            Paragraph("<b>จำนวน (คัน)</b>", style_cell_bold),
            Paragraph("<b>ราคาต่อหน่วย (บาท)</b>", style_cell_bold),
            Paragraph("<b>จำนวนเงิน (บาท)</b>", style_cell_bold)
        ],
        [
            Paragraph("1", style_cell),
            Paragraph("BK-AT-06", style_cell),
            Paragraph("PCX 160", style_cell),
            Paragraph("1", style_cell),
            Paragraph("93,400.00", style_cell),
            Paragraph("93,400.00", style_cell)
        ],
        [
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("<b>ราคาสินค้าก่อนภาษีมูลค่าเพิ่ม (Price before VAT)</b>", style_cell),
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("87,289.72", style_cell)
        ],
        [
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("<b>ภาษีมูลค่าเพิ่ม 7% (VAT 7%)</b>", style_cell),
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("6,110.28", style_cell)
        ],
        [
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("<b>ค่าจัดส่งและขนส่ง (Shipping & Delivery)</b>", style_cell),
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("0.00 (ฟรี/รับที่ร้าน)", style_cell)
        ],
        [
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("<b>จำนวนเงินรวมทั้งสิ้น (Grand Total)</b>", style_cell_bold),
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph("฿93,400.00", style_cell_right_bold)
        ]
    ]
    items_table = Table(table_data, colWidths=[1.0 * cm, 2.3 * cm, 6.3 * cm, 2.0 * cm, 3.2 * cm, 3.2 * cm])
    t_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, 1), 0.5, colors.HexColor('#dee2e6')),
        ('SPAN', (2, 2), (4, 2)),
        ('SPAN', (2, 3), (4, 3)),
        ('SPAN', (2, 4), (4, 4)),
        ('SPAN', (2, 5), (4, 5)),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fef2f2')),
        ('LINEABOVE', (2, 5), (-1, 5), 1, colors.HexColor('#cc0000')),
        ('LINEBELOW', (2, 5), (-1, 5), 1.5, colors.HexColor('#cc0000')),
    ]
    items_table.setStyle(TableStyle(t_styles))
    story.append(items_table)
    story.append(Spacer(1, 0.6 * cm))

    # Terms & Signature
    sign_data = [
        [
            Paragraph(
                "<b>เงื่อนไขและข้อกำหนด:</b><br/>"
                "• รถจักรยานยนต์ทุกคันผ่านการตรวจเช็กมาตรฐานก่อนส่งมอบแก่ลูกค้า<br/>"
                "• โปรดเก็บเอกสารนี้ไว้เป็นหลักฐานประกอบการรับประกันและจดทะเบียนรถ<br/>"
                "• เอกสารนี้เป็นใบเสร็จรับเงิน/ใบส่งมอบสินค้า (ไม่ใช่ใบกำกับภาษีเต็มรูปตามมาตรา 86/4 แห่งประมวลรัษฎากร)",
                style_cell
            ),
            Paragraph(
                "<br/>ลงชื่อ ...................................................<br/>"
                "( ผู้มีอำนาจลงนาม / ตัวแทนร้านค้า )<br/>"
                "160 ธีระ สายซิ่ง",
                style_cell
            )
        ]
    ]
    sign_table = Table(sign_data, colWidths=[10 * cm, 8 * cm])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sign_table)

    doc.build(story)
    print(f"Generated {filename}")

build_test_pdf('SarabunTH', 'SarabunTH-Bold', 'scratch/receipt_sarabun_shaped.pdf')
build_test_pdf('TahomaTH', 'TahomaTH-Bold', 'scratch/receipt_tahoma_shaped.pdf')

for name in ['receipt_sarabun_shaped', 'receipt_tahoma_shaped']:
    doc = fitz.open(f'scratch/{name}.pdf')
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    pix.save(f'scratch/{name}.png')
print("Rendered PNGs!")
