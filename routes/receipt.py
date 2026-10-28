"""
routes/receipt.py
โมดูลสร้างใบเสร็จรับเงินและใบส่งมอบสินค้า PDF ด้วย ReportLab (Pure Python)
รองรับภาษาไทย 100% สระและวรรณยุกต์ไม่ซ้อนทับกันด้วย OpenType Complex Script Shaping (uharfbuzz)
ใช้ฟอนต์ Tahoma (tahoma.ttf, tahomabd.ttf) ใน static/fonts/ และ Sarabun เป็นฟอนต์ทางการ
"""

import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# กำหนดเส้นทางฟอนต์ภาษาไทยสำหรับใบเสร็จ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

TAHOMA_REGULAR = os.path.join(FONT_DIR, 'tahoma.ttf')
TAHOMA_BOLD = os.path.join(FONT_DIR, 'tahomabd.ttf')
SARABUN_REGULAR = os.path.join(FONT_DIR, 'Sarabun-Regular.ttf')
SARABUN_BOLD = os.path.join(FONT_DIR, 'Sarabun-Bold.ttf')

# ตัวแปรสถานะการลงทะเบียนฟอนต์
_font_registered = False
_primary_font_name = 'ThaiFont'
_bold_font_name = 'ThaiFont-Bold'


def _create_and_register_font(name, filepath):
    """สร้างและลงทะเบียนฟอนต์ พร้อมกำหนด Private Range ใน Subset 0 เพื่อป้องกันปัญหากล่องสี่เหลี่ยม [ ]"""
    font = TTFont(name, filepath, shapable=True)
    try:
        _ = font.hbFace
        font._TTFont__hbPrivate = 0x0080
    except Exception:
        pass
    pdfmetrics.registerFont(font)
    return font


def register_thai_fonts():
    """
    ลงทะเบียนฟอนต์ภาษาไทยพร้อมเปิดใช้งาน shapable=True สำหรับ uharfbuzz
    จัดวางสระบน-ล่าง วรรณยุกต์ ไม่ซ้อนทับกัน และไม่เกิดปัญหาสระลอยหรือกล่องสี่เหลี่ยม
    """
    global _font_registered, _primary_font_name, _bold_font_name
    if _font_registered:
        return _primary_font_name, _bold_font_name

    # 1. ใช้ Tahoma ใน static/fonts/ (หรือ Windows Fonts) เป็นอันดับแรก
    tahoma_reg = TAHOMA_REGULAR if os.path.exists(TAHOMA_REGULAR) else 'C:\\Windows\\Fonts\\tahoma.ttf'
    tahoma_bd = TAHOMA_BOLD if os.path.exists(TAHOMA_BOLD) else 'C:\\Windows\\Fonts\\tahomabd.ttf'

    if os.path.exists(tahoma_reg):
        try:
            _create_and_register_font('ThaiFont', tahoma_reg)
            if os.path.exists(tahoma_bd):
                _create_and_register_font('ThaiFont-Bold', tahoma_bd)
                _bold_font_name = 'ThaiFont-Bold'
            else:
                _bold_font_name = 'ThaiFont'
            _primary_font_name = 'ThaiFont'
            _font_registered = True
            return _primary_font_name, _bold_font_name
        except Exception as e:
            print(f"Warning: could not register Tahoma font: {e}")

    # 2. ฟอนต์ Sarabun ใน static/fonts/
    if os.path.exists(SARABUN_REGULAR):
        try:
            _create_and_register_font('ThaiFont', SARABUN_REGULAR)
            if os.path.exists(SARABUN_BOLD):
                _create_and_register_font('ThaiFont-Bold', SARABUN_BOLD)
                _bold_font_name = 'ThaiFont-Bold'
            else:
                _bold_font_name = 'ThaiFont'
            _primary_font_name = 'ThaiFont'
            _font_registered = True
            return _primary_font_name, _bold_font_name
        except Exception as e:
            print(f"Warning: could not register Sarabun font: {e}")

    return 'Helvetica', 'Helvetica-Bold'


def calculate_vat_breakdown(order):
    """
    คำนวณและแจกแจงภาษีมูลค่าเพิ่ม (VAT 7%) แยกกรณีราคาก่อน VAT และราคารวม VAT แล้ว
    - กรณีราคาก่อน VAT (VAT-exclusive): เช่น 86,862 -> VAT 7% = 6,080.34, รวม VAT = 92,942.34
    - กรณีราคารวม VAT แล้ว (VAT-inclusive): เช่น 93,400 -> ถอดก่อน VAT = 93,400 / 1.07 = 87,289.72, VAT = 6,110.28
    """
    order = dict(order)
    subtotal = float(order['subtotal']) if order.get('subtotal') is not None else float(order['total_amount'])
    discount = float(order['discount']) if order.get('discount') is not None else 0.0
    shipping_fee = float(order['shipping_fee']) if order.get('shipping_fee') is not None else 0.0
    vat_rate = float(order['vat_rate']) if order.get('vat_rate') is not None else 0.07
    total_amount = float(order['total_amount'])

    taxable = max(0.0, subtotal - discount)
    expected_exc_vat = round(taxable * vat_rate, 2)
    expected_exc_total = round(taxable + expected_exc_vat + shipping_fee, 2)
    expected_inc_total = round(taxable + shipping_fee, 2)

    if abs(total_amount - expected_exc_total) < 0.05 and abs(total_amount - expected_inc_total) >= 0.05:
        # กรณีราคาก่อน VAT (VAT-exclusive)
        net_before_vat = round(taxable, 2)
        vat_amount = round(taxable * vat_rate, 2)
        grand_total = round(net_before_vat + vat_amount + shipping_fee, 2)
        is_vat_inclusive = False
    else:
        # กรณีราคารวม VAT แล้ว (VAT-inclusive) - ระบบหลักของร้าน
        net_before_vat = round(taxable / (1.0 + vat_rate), 2)
        vat_amount = round(taxable - net_before_vat, 2)
        grand_total = round(taxable + shipping_fee, 2)
        is_vat_inclusive = True

    if order.get('vat_amount') is not None and float(order['vat_amount']) > 0:
        vat_amount = float(order['vat_amount'])
        if abs(total_amount - (taxable + shipping_fee)) < 0.05:
            net_before_vat = round(taxable - vat_amount, 2)
            grand_total = round(taxable + shipping_fee, 2)

    return {
        'net_before_vat': net_before_vat,
        'vat_amount': vat_amount,
        'grand_total': grand_total,
        'is_vat_inclusive': is_vat_inclusive,
        'discount': discount,
        'shipping_fee': shipping_fee,
        'vat_rate': vat_rate
    }


def generate_receipt_pdf(order, items, receipt_number, payment=None):
    """
    สร้างไฟล์ใบเสร็จรับเงินและใบส่งมอบสินค้า PDF ในรูปแบบ BytesIO
    :param order: sqlite3.Row หรือ dict ของตาราง orders
    :param items: รายการของ sqlite3.Row หรือ dict ของตาราง order_items
    :param receipt_number: เลขที่ใบเสร็จ เช่น REC-20261027-0001
    :param payment: ข้อมูลการชำระเงิน (ถ้ามี)
    :return: BytesIO buffer ของ PDF
    """
    regular_font, bold_font = register_thai_fonts()
    order = dict(order)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    story = []

    # สไตล์ตัวหนังสือฟอนต์ภาษาไทย (wordWrap='LTR' และ shaping=True ให้ uharfbuzz จัดวางสระ/วรรณยุกต์ถูกต้อง)
    style_shop_info = ParagraphStyle(
        name='ShopInfo',
        fontName=regular_font,
        fontSize=10.5,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#222222')
    )
    style_receipt_meta = ParagraphStyle(
        name='ReceiptMeta',
        fontName=regular_font,
        fontSize=10.5,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        alignment=2,  # ชิดขวา
        textColor=colors.HexColor('#222222')
    )
    style_cell = ParagraphStyle(
        name='CellText',
        fontName=regular_font,
        fontSize=10,
        leading=15,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#222222')
    )
    style_cell_bold = ParagraphStyle(
        name='CellTextBold',
        fontName=bold_font,
        fontSize=10,
        leading=15,
        wordWrap='LTR',
        shaping=True,
        textColor=colors.HexColor('#111111')
    )
    style_cell_right = ParagraphStyle(
        name='CellTextRight',
        fontName=regular_font,
        fontSize=10,
        leading=15,
        wordWrap='LTR',
        shaping=True,
        alignment=2,
        textColor=colors.HexColor('#222222')
    )
    style_cell_right_bold = ParagraphStyle(
        name='CellTextRightBold',
        fontName=bold_font,
        fontSize=11,
        leading=16,
        wordWrap='LTR',
        shaping=True,
        alignment=2,
        textColor=colors.HexColor('#cc0000')
    )
    style_footer = ParagraphStyle(
        name='FooterNote',
        fontName=regular_font,
        fontSize=9,
        leading=14,
        wordWrap='LTR',
        shaping=True,
        alignment=1,  # กึ่งกลาง
        textColor=colors.HexColor('#555555')
    )

    # 1. Header (ข้อมูลร้าน 160 ธีระ สายซิ่ง และ เลขที่ใบเสร็จ)
    header_data = [
        [
            Paragraph(
                "<b>160 ธีระ สายซิ่ง (160 Teera Sai Sing)</b><br/>"
                "ศูนย์จำหน่ายรถจักรยานยนต์มาตรฐาน (ขนาดไม่เกิน 160 cc)<br/>"
                "899/22 หมู่บ้านศรีมงคล ต.ศิลา อ.เมืองขอนแก่น จ.ขอนแก่น 40000<br/>"
                "โทร: 065-718-2338 | Facebook: Teera Jantharasorn<br/>"
                "เวลาทำการ: วันพุธ 09:00 - 18:00 น.",
                style_shop_info
            ),
            Paragraph(
                "<b>ใบเสร็จรับเงิน / ใบส่งมอบสินค้า</b><br/>"
                f"<b>เลขที่เอกสาร:</b> {receipt_number}<br/>"
                f"<b>เลขที่คำสั่งซื้อ:</b> {order['order_number']}<br/>"
                f"<b>วันที่ออกเอกสาร:</b> {str(order['created_at'])[:19]}",
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

    # 2. ข้อมูลลูกค้า และ ข้อมูลการชำระเงิน / จัดส่ง
    payment_status_text = "ชำระเงินเรียบร้อยแล้ว"
    if payment and payment['status'] == 'approved':
        verified_date = str(payment['verified_at'])[:19] if payment['verified_at'] else 'ตรวจสอบแล้ว'
        payment_status_text = f"ชำระเงินแล้ว (ยืนยันเมื่อ {verified_date})"

    shipping_method_label = "รับรถที่ร้าน (ศูนย์ขอนแก่น)" if order['shipping_method'] == 'pickup' else "จัดส่งระยะไกล"
    delivery_notes_text = f"<br/><b>หมายเหตุจัดส่ง:</b> {order['delivery_notes']}" if order.get('delivery_notes') else ""

    cust_info = [
        [
            Paragraph(
                f"<b>ข้อมูลลูกค้าผู้ซื้อ:</b><br/>"
                f"<b>ชื่อ-นามสกุล:</b> {order['customer_name']}<br/>"
                f"<b>เบอร์โทรศัพท์:</b> {order['customer_phone']}<br/>"
                f"<b>วิธีรับสินค้า:</b> {shipping_method_label}<br/>"
                f"<b>ที่อยู่:</b> {order['customer_address']}{delivery_notes_text}",
                style_cell
            ),
            Paragraph(
                f"<b>ข้อมูลการชำระเงิน:</b><br/>"
                f"<b>สถานะการชำระ:</b> <font color='#059669'><b>[√] {payment_status_text}</b></font><br/>"
                f"<b>วิธีชำระเงิน:</b> โอนเงินผ่านธนาคารพร้อมหลักฐานสลิป<br/>"
                f"<b>สถานะคำสั่งซื้อ:</b> {order['status']}",
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

    # 3. ตารางรายการสินค้า
    table_data = [
        [
            Paragraph("<b>ลำดับ</b>", style_cell_bold),
            Paragraph("<b>รหัสสินค้า</b>", style_cell_bold),
            Paragraph("<b>รายการรุ่นรถจักรยานยนต์</b>", style_cell_bold),
            Paragraph("<b>จำนวน (คัน)</b>", style_cell_right_bold),
            Paragraph("<b>ราคาต่อหน่วย (บาท)</b>", style_cell_right_bold),
            Paragraph("<b>จำนวนเงิน (บาท)</b>", style_cell_right_bold)
        ]
    ]

    for idx, item in enumerate(items, 1):
        table_data.append([
            Paragraph(str(idx), style_cell),
            Paragraph(str(item['product_code'] or '-'), style_cell),
            Paragraph(str(item['product_name']), style_cell),
            Paragraph(str(item['quantity']), style_cell_right),
            Paragraph(f"{float(item['price']):,.2f}", style_cell_right),
            Paragraph(f"{float(item['subtotal']):,.2f}", style_cell_right)
        ])

    # 4. คำนวณและสรุปยอดเงิน (รองรับทั้งกรณีราคารวม VAT และราคาก่อน VAT ไม่คิด VAT ซ้ำ)
    vat_info = calculate_vat_breakdown(order)
    net_before_vat = vat_info['net_before_vat']
    vat_amount = vat_info['vat_amount']
    grand_total = vat_info['grand_total']
    discount = vat_info['discount']
    shipping_fee = vat_info['shipping_fee']
    vat_rate = vat_info['vat_rate']

    # โครงสร้างแถวสรุปยอดเงิน
    summary_rows_def = [
        ("<b>ราคาสินค้าก่อนภาษีมูลค่าเพิ่ม (Price before VAT)</b>", f"{net_before_vat:,.2f}", style_cell, style_cell_right, False)
    ]

    if discount > 0:
        summary_rows_def.append(("<b>ส่วนลด (Discount)</b>", f"-{discount:,.2f}", style_cell, style_cell_right, False))

    summary_rows_def.append((f"<b>ภาษีมูลค่าเพิ่ม {int(vat_rate * 100)}% (VAT {int(vat_rate * 100)}%)</b>", f"{vat_amount:,.2f}", style_cell, style_cell_right, False))

    ship_text = f"{shipping_fee:,.2f}" if shipping_fee > 0 else "0.00 (ฟรี/รับที่ร้าน)"
    summary_rows_def.append(("<b>ค่าจัดส่งและขนส่ง (Shipping & Delivery)</b>", ship_text, style_cell, style_cell_right, False))

    summary_rows_def.append(("<b>จำนวนเงินรวมทั้งสิ้น (Grand Total)</b>", f"<b>฿{grand_total:,.2f}</b>", style_cell_bold, style_cell_right_bold, True))

    grand_total_row_idx = None
    for label, val, l_style, r_style, is_gt in summary_rows_def:
        current_idx = len(table_data)
        if is_gt:
            grand_total_row_idx = current_idx
        table_data.append([
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph(label, l_style),
            Paragraph("", style_cell),
            Paragraph("", style_cell),
            Paragraph(val, r_style)
        ])

    items_table = Table(table_data, colWidths=[1.0 * cm, 2.3 * cm, 6.3 * cm, 2.0 * cm, 3.2 * cm, 3.2 * cm])
    t_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, len(items)), 0.5, colors.HexColor('#dee2e6')),
    ]
    # ผสานคอลัมน์ 2 ถึง 4 ในทุกแถวสรุปยอด
    for r_idx in range(len(items) + 1, len(table_data)):
        t_styles.append(('SPAN', (2, r_idx), (4, r_idx)))

    if grand_total_row_idx is not None:
        t_styles.append(('BACKGROUND', (0, grand_total_row_idx), (-1, grand_total_row_idx), colors.HexColor('#fef2f2')))
        t_styles.append(('LINEABOVE', (2, grand_total_row_idx), (-1, grand_total_row_idx), 1, colors.HexColor('#cc0000')))
        t_styles.append(('LINEBELOW', (2, grand_total_row_idx), (-1, grand_total_row_idx), 1.5, colors.HexColor('#cc0000')))

    items_table.setStyle(TableStyle(t_styles))
    story.append(items_table)
    story.append(Spacer(1, 0.6 * cm))

    # 5. ลายเซ็นและตราประทับ
    sign_data = [
        [
            Paragraph(
                "<b>เงื่อนไขและข้อกำหนด:</b><br/>"
                "• รถจักรยานยนต์ทุกคันผ่านการตรวจเช็กมาตรฐานก่อนส่งมอบแก่ลูกค้า<br/>"
                "• โปรดเก็บเอกสารนี้ ไว้เป็นหลักฐานประกอบการรับประกันและจดทะเบียนรถ<br/>"
                "• เอกสารนี้เป็นใบเสร็จรับเงิน/ใบส่งมอบสินค้า (ไม่ใช่ใบกำกับภาษีเต็มรูปตามมาตรา 86/4 แห่งประมวลรัษฎากร)",
                style_cell
            ),
            Paragraph(
                "<br/>ลงชื่อ ...................................................<br/>"
                "( ผู้มีอำนาจลงนาม / ตัวแทนร้านค้า )<br/>"
                "160 ธีระ สายซิ่ง",
                style_cell_right
            )
        ]
    ]
    sign_table = Table(sign_data, colWidths=[10 * cm, 8 * cm])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sign_table)
    story.append(Spacer(1, 0.4 * cm))

    # 6. ท้ายกระดาษ
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc'), spaceBefore=6, spaceAfter=6))
    story.append(Paragraph("160 ธีระ สายซิ่ง (160 Teera Sai Sing) • ศูนย์จำหน่ายรถจักรยานยนต์มาตรฐานไม่เกิน 160 cc • โทร 065-718-2338", style_footer))

    doc.build(story)
    buffer.seek(0)
    return buffer
