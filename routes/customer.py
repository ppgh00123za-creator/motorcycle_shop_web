"""
routes/customer.py
ระบบสั่งซื้อ (Checkout), ชำระเงินแนบสลิป, ประวัติคำสั่งซื้อ, ยกเลิกคำสั่งซื้อ และดาวน์โหลดใบเสร็จ PDF
"""

import os
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, abort
from database import get_db_connection, log_order_status
from routes.auth import login_required
from routes.receipt import generate_receipt_pdf
from routes.helpers import allowed_file

customer_bp = Blueprint('customer', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIP_UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'ไฟล์ที่ผู้ใช้อัปโหลด', 'slips')


import uuid
from config import SHOP_CONFIG, VAT_RATE, DEFAULT_DELIVERY_FEE

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    หน้ายืนยันการสั่งซื้อ:
    - คำนวณ VAT 7% ณ ขั้นตอนสั่งซื้อเท่านั้น (ราคาสินค้าหน้าร้านเป็นราคาดิบ)
    - รองรับ 2 วิธีรับสินค้า: 1) รับรถที่ร้าน (ฟรี) 2) จัดส่งระยะไกล
    - บันทึกข้อมูลราคา, VAT, ค่าจัดส่ง, และยอดสุทธิแบบ Snapshot ลงคำสั่งซื้อ
    - ป้องกันการส่งซ้ำและตัดสต็อกซ้ำด้วย Idempotency Token
    - ใช้ Database Transaction ในการตัดสต็อก
    """
    cart = session.get('cart', {})
    if not cart:
        flash('ตะกร้าสินค้าว่างเปล่า กรุณาเลือกสินค้าก่อนสั่งซื้อ', 'warning')
        return redirect(url_for('shop.products'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    # รวบรวมข้อมูลสินค้าและคำนวณยอดรวมสินค้าก่อน VAT
    checkout_items = []
    items_subtotal = 0.0

    for p_id_str, qty in cart.items():
        try:
            p_id = int(p_id_str)
        except ValueError:
            continue
        product = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
        if not product or product['status'] == 'discontinued':
            conn.close()
            flash('สินค้าบางรายการไม่สามารถสั่งซื้อได้ กรุณาตรวจสอบตะกร้าสินค้า', 'danger')
            return redirect(url_for('shop.cart'))

        if product['stock'] < qty:
            conn.close()
            flash(f'สินค้า {product["model"]} มีสต็อกไม่เพียงพอ (คงเหลือ {product["stock"]} คัน)', 'danger')
            return redirect(url_for('shop.cart'))

        sub = float(product['price']) * int(qty)
        items_subtotal += sub
        checkout_items.append({
            'product': product,
            'quantity': qty,
            'price': float(product['price']),
            'subtotal': sub
        })

    # คำนวณ VAT 7% ฝั่งเซิร์ฟเวอร์ (รวม VAT อยู่ในราคาสินค้าแล้ว)
    discount = 0.0
    vat_rate = float(VAT_RATE)
    taxable = max(0.0, items_subtotal - discount)
    net_before_vat = round(taxable / (1.0 + vat_rate), 2)
    vat_amount = round(taxable - net_before_vat, 2)

    # วิธีรับสินค้าเริ่มต้น หรือจาก Form / Query
    shipping_method = request.form.get('shipping_method') if request.method == 'POST' else request.args.get('method', 'pickup')
    if shipping_method not in ('pickup', 'delivery'):
        shipping_method = 'pickup'

    shipping_estimate_choice = request.form.get('shipping_estimate_choice', 'standard')
    if shipping_method == 'delivery':
        if shipping_estimate_choice == 'custom_estimate':
            shipping_fee = 0.0
            is_shipping_estimated = 1
        else:
            shipping_fee = float(DEFAULT_DELIVERY_FEE)
            is_shipping_estimated = 0
    else:
        shipping_fee = 0.0
        is_shipping_estimated = 0

    # ยอดชำระรวม = ยอดรวมสินค้า (รวม VAT แล้ว) - ส่วนลด + ค่าจัดส่งที่ยืนยันแล้ว (ไม่บวก VAT ซ้ำ)
    grand_total = round(items_subtotal - discount + shipping_fee, 2)

    if request.method == 'POST':
        # ป้องกันการส่งซ้ำ (Idempotency Token Protection)
        submitted_token = request.form.get('checkout_token', '').strip()
        expected_token = session.get('checkout_token')
        if not submitted_token or submitted_token != expected_token:
            conn.close()
            flash('คำสั่งซื้อนี้กำลังประมวลผลหรือได้รับการบันทึกแล้ว กรุณาตรวจสอบประวัติคำสั่งซื้อ', 'info')
            return redirect(url_for('customer.orders'))

        customer_name = request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_address = request.form.get('customer_address', '').strip()
        delivery_notes = request.form.get('delivery_notes', '').strip()

        if not customer_name or not customer_phone or not customer_address:
            conn.close()
            flash('กรุณากรอกข้อมูลชื่อ เบอร์โทรศัพท์ และที่อยู่ให้ครบถ้วน', 'danger')
            return render_template('checkout.html',
                                   user=user,
                                   items=checkout_items,
                                   items_subtotal=items_subtotal,
                                   discount=discount,
                                   net_before_vat=net_before_vat,
                                   vat_rate=vat_rate,
                                   vat_amount=vat_amount,
                                   shipping_method=shipping_method,
                                   shipping_fee=shipping_fee,
                                   is_shipping_estimated=is_shipping_estimated,
                                   grand_total=grand_total,
                                   checkout_token=expected_token)

        # เคลียร์ Token เพื่อไม่ให้ส่งซ้ำได้อีก
        session.pop('checkout_token', None)

        # เริ่มต้น Database Transaction ป้องกัน Race Condition
        cursor = conn.cursor()
        try:
            # 1. ตรวจสอบสต็อกอีกครั้งภายใต้ Transaction
            for item in checkout_items:
                p_id = item['product']['id']
                cur_p = cursor.execute("SELECT stock, model, status FROM products WHERE id = ?", (p_id,)).fetchone()
                if not cur_p or cur_p['stock'] < item['quantity'] or cur_p['status'] != 'available':
                    raise ValueError(f"สินค้า {item['product']['model']} สต็อกไม่เพียงพอในขณะนี้")

            # 2. สร้างหมายเลขคำสั่งซื้อที่ไม่ซ้ำกัน
            date_prefix = datetime.now().strftime('%Y%m%d')
            cursor.execute("SELECT COUNT(*) FROM orders WHERE order_number LIKE ?", (f"ORD-{date_prefix}-%",))
            count_today = cursor.fetchone()[0] + 1
            order_number = f"ORD-{date_prefix}-{count_today:04d}"

            # 3. บันทึกคำสั่งซื้อลงตาราง orders พร้อม Snapshot ราคา, VAT, ค่าจัดส่ง
            cursor.execute("""
                INSERT INTO orders (
                    order_number, user_id, customer_name, customer_phone, customer_address,
                    total_amount, status, subtotal, discount, vat_rate, vat_amount,
                    shipping_method, shipping_fee, is_shipping_estimated, delivery_notes, is_restocked
                ) VALUES (?, ?, ?, ?, ?, ?, 'รอชำระเงิน', ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                order_number, session['user_id'], customer_name, customer_phone, customer_address,
                grand_total, items_subtotal, discount, vat_rate, vat_amount,
                shipping_method, shipping_fee, is_shipping_estimated, delivery_notes
            ))
            order_id = cursor.lastrowid

            # 4. บันทึกรายการสินค้าใน order_items และตัดสต็อกสินค้าใน products
            for item in checkout_items:
                p_id = item['product']['id']
                qty = item['quantity']
                sub = item['subtotal']
                unit_price = item['price']

                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, product_code, product_name, price, quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (order_id, p_id, item['product']['code'], item['product']['model'], unit_price, qty, sub))

                # ดึงสต็อกเดิมก่อนตัด
                cur_p = cursor.execute("SELECT stock FROM products WHERE id = ?", (p_id,)).fetchone()
                old_stock = cur_p['stock']
                new_stock = old_stock - qty

                # ตัดสต็อกและปรับสถานะหากสินค้าหมด
                cursor.execute("""
                    UPDATE products 
                    SET stock = ?,
                        status = CASE WHEN ? <= 0 THEN 'out_of_stock' ELSE status END
                    WHERE id = ?
                """, (new_stock, new_stock, p_id))

                # บันทึกประวัติการปรับปรุงสต็อก (Audit Log)
                cursor.execute("""
                    INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_id, old_stock, new_stock, -qty, f"ตัดสต็อกคำสั่งซื้อ {order_number}", session['user_id'], customer_name))

            # 5. บันทึกประวัติสถานะคำสั่งซื้อ (order_status_history)
            ship_desc = "รับรถที่ศูนย์ขอนแก่น" if shipping_method == 'pickup' else "จัดส่งระยะไกล"
            log_order_status(conn, order_id, 'รอชำระเงิน', f'สร้างคำสั่งซื้อสำเร็จ ({ship_desc}) รวมทั้งสิ้น ฿{grand_total:,.2f} รอแนบสลิปชำระเงิน', customer_name)

            # บันทึก Transaction ลงฐานข้อมูล
            conn.commit()

            # ล้างตะกร้าสินค้าหลังสั่งซื้อสำเร็จ
            session.pop('cart', None)
            conn.close()

            flash(f'สั่งซื้อสำเร็จ! เลขที่คำสั่งซื้อของคุณคือ {order_number}', 'success')
            return redirect(url_for('customer.order_detail', order_id=order_id))

        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'เกิดข้อผิดพลาดในการสร้างคำสั่งซื้อ: {str(e)}', 'danger')
            return redirect(url_for('shop.cart'))

    # สร้าง Token สำหรับป้องกัน Double Submit
    checkout_token = uuid.uuid4().hex
    session['checkout_token'] = checkout_token

    conn.close()
    return render_template('checkout.html',
                           user=user,
                           items=checkout_items,
                           items_subtotal=items_subtotal,
                           discount=discount,
                           net_before_vat=net_before_vat,
                           vat_rate=vat_rate,
                           vat_amount=vat_amount,
                           shipping_method=shipping_method,
                           shipping_fee=shipping_fee,
                           is_shipping_estimated=is_shipping_estimated,
                           grand_total=grand_total,
                           checkout_token=checkout_token)


@customer_bp.route('/orders')
@login_required
def orders():
    """แสดงประวัติคำสั่งซื้อเฉพาะของบัญชีตนเอง (คงเหลือเฉพาะ 3 ออเดอร์ล่าสุดที่เสร็จสิ้น และออเดอร์ที่ยังไม่เสร็จสิ้นทั้งหมด)"""
    conn = get_db_connection()
    show_archived = request.args.get('show_archived', '0') == '1'

    if show_archived:
        user_orders = conn.execute("""
            SELECT o.*, 
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
                   (SELECT status FROM payments WHERE order_id = o.id) as payment_status
            FROM orders o
            WHERE o.user_id = ? AND o.is_archived = 1
            ORDER BY o.id DESC
        """, (session['user_id'],)).fetchall()
    else:
        user_orders = conn.execute("""
            SELECT o.*, 
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
                   (SELECT status FROM payments WHERE order_id = o.id) as payment_status
            FROM orders o
            WHERE o.user_id = ? AND o.is_archived = 0
            ORDER BY o.id DESC
        """, (session['user_id'],)).fetchall()

    archived_count = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND is_archived = 1",
        (session['user_id'],)
    ).fetchone()[0]

    conn.close()

    return render_template('orders.html', orders=user_orders, show_archived=show_archived, archived_count=archived_count)


@customer_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """แสดงรายละเอียดคำสั่งซื้อ ตรวจสอบสิทธิ์เจ้าของคำสั่งซื้อ และดูสถานะสลิป"""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อที่ระบุ', 'danger')
        return redirect(url_for('customer.orders'))

    # ตรวจสอบสิทธิ์: ลูกค้าดูได้เฉพาะคำสั่งซื้อของตนเอง (แอดมินดูได้ทุกคน)
    if order['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        conn.close()
        flash('คุณไม่มีสิทธิ์เข้าดูคำสั่งซื้อของผู้อื่น', 'danger')
        return redirect(url_for('customer.orders'))

    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    payment = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,)).fetchone()
    history = conn.execute("SELECT * FROM order_status_history WHERE order_id = ? ORDER BY id ASC", (order_id,)).fetchall()
    receipt = conn.execute("SELECT * FROM receipts WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()

    return render_template('order_detail.html', 
                           order=order, 
                           items=items, 
                           payment=payment, 
                           history=history,
                           receipt=receipt)


@customer_bp.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
def pay_order(order_id):
    """แนบสลิปหลักฐานการชำระเงินสำหรับคำสั่งซื้อ"""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order or order['user_id'] != session['user_id']:
        conn.close()
        flash('ไม่พบคำสั่งซื้อหรือไม่มีสิทธิ์ดำเนินการ', 'danger')
        return redirect(url_for('customer.orders'))

    if order['status'] in ['ชำระเงินแล้ว', 'จัดส่งแล้ว', 'ยกเลิก']:
        conn.close()
        flash('คำสั่งซื้อนี้ไม่อยู่ในสถานะที่สามารถแนบสลิปได้', 'warning')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    # ตรวจสอบไฟล์ที่อัปโหลด
    if 'slip_file' not in request.files:
        conn.close()
        flash('กรุณาเลือกไฟล์รูปภาพสลิป', 'danger')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    file = request.files['slip_file']
    if file.filename == '':
        conn.close()
        flash('ยังไม่ได้เลือกไฟล์รูปภาพ', 'danger')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    if not allowed_file(file.filename):
        conn.close()
        flash('อนุญาตเฉพาะไฟล์รูปภาพนามสกุล .png, .jpg, .jpeg, .webp เท่านั้น', 'danger')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    os.makedirs(SLIP_UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_filename = f"slip_{order['id']}_{int(time.time())}.{ext}"
    filepath = os.path.join(SLIP_UPLOAD_DIR, safe_filename)
    file.save(filepath)

    cursor = conn.cursor()
    # ตรวจสอบว่าเคยมีรายการชำระเงินหรือยัง (กรณีถูกปฏิเสธแล้วแนบใหม่)
    existing_pay = cursor.execute("SELECT id FROM payments WHERE order_id = ?", (order_id,)).fetchone()
    if existing_pay:
        cursor.execute("""
            UPDATE payments 
            SET slip_image = ?, status = 'pending', reject_reason = NULL, payment_date = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (safe_filename, order_id))
    else:
        cursor.execute("""
            INSERT INTO payments (order_id, slip_image, amount, status)
            VALUES (?, ?, ?, 'pending')
        """, (order_id, safe_filename, order['total_amount']))

    # อัปเดตสถานะคำสั่งซื้อเป็น "รอตรวจสอบการชำระเงิน"
    cursor.execute("""
        UPDATE orders 
        SET status = 'รอตรวจสอบการชำระเงิน', updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (order_id,))

    # บันทึกประวัติสถานะ
    log_order_status(conn, order_id, 'รอตรวจสอบการชำระเงิน', 'ลูกค้าแนบสลิปหลักฐานการโอนเงิน รอเจ้าหน้าที่ตรวจสอบยอดเงิน', session.get('user_name', 'ลูกค้า'))
    conn.commit()
    conn.close()

    flash('แนบหลักฐานการชำระเงินสำเร็จแล้ว! เจ้าหน้าที่จะตรวจสอบยอดเงินโดยเร็วที่สุด', 'success')
    return redirect(url_for('customer.order_detail', order_id=order_id))


@customer_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """ลูกค้ายกเลิกคำสั่งซื้อ และคืนสต็อกสินค้าเพียงครั้งเดียวด้วย Database Transaction และบันทึก Audit Log"""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order or order['user_id'] != session['user_id']:
        conn.close()
        flash('ไม่พบคำสั่งซื้อหรือไม่มีสิทธิ์ดำเนินการ', 'danger')
        return redirect(url_for('customer.orders'))

    # อนุญาตให้ยกเลิกได้เฉพาะเมื่อยังไม่ได้อนุมัติเงิน (รอชำระเงิน หรือ รอตรวจสอบ)
    if order['status'] not in ['รอชำระเงิน', 'รอตรวจสอบการชำระเงิน']:
        conn.close()
        flash(f'ไม่สามารถยกเลิกคำสั่งซื้อในสถานะ "{order["status"]}" ได้', 'danger')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    cursor = conn.cursor()
    try:
        # ตรวจสอบว่าเคยคืนสต็อกไปแล้วหรือยัง (คืนเพียงครั้งเดียวเท่านั้น)
        if not order['is_restocked']:
            items = cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
            for it in items:
                cur_p = cursor.execute("SELECT stock FROM products WHERE id = ?", (it['product_id'],)).fetchone()
                if cur_p:
                    old_stock = cur_p['stock']
                    new_stock = old_stock + it['quantity']
                    cursor.execute("""
                        UPDATE products 
                        SET stock = ?,
                            status = CASE WHEN status = 'out_of_stock' THEN 'available' ELSE status END
                        WHERE id = ?
                    """, (new_stock, it['product_id']))

                    # บันทึกประวัติการปรับสต็อก
                    cursor.execute("""
                        INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (it['product_id'], old_stock, new_stock, it['quantity'], f"คืนสต็อกจากการยกเลิกคำสั่งซื้อ {order['order_number']}", session['user_id'], session.get('user_name', 'ลูกค้า')))

        # อัปเดตสถานะคำสั่งซื้อเป็น "ยกเลิก" และทำเครื่องหมายว่าคืนสต็อกแล้ว
        cursor.execute("UPDATE orders SET status = 'ยกเลิก', is_restocked = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))

        # บันทึกประวัติสถานะ
        log_order_status(conn, order_id, 'ยกเลิก', 'ลูกค้ายกเลิกคำสั่งซื้อ ระบบได้คืนสต็อกสินค้าเรียบร้อยแล้ว', session.get('user_name', 'ลูกค้า'))
        conn.commit()
        flash('ยกเลิกคำสั่งซื้อและคืนสต็อกสินค้าเรียบร้อยแล้ว', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'เกิดข้อผิดพลาดในการยกเลิก: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('customer.order_detail', order_id=order_id))


@customer_bp.route('/order/<int:order_id>/receipt')
@login_required
def download_receipt(order_id):
    """ดาวน์โหลดใบเสร็จ PDF เมื่อการชำระเงินได้รับการอนุมัติแล้วเท่านั้น"""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อ', 'danger')
        return redirect(url_for('customer.orders'))

    # ตรวจสอบสิทธิ์การเข้าถึง
    if order['user_id'] != session['user_id'] and session.get('user_role') != 'admin':
        conn.close()
        flash('คุณไม่มีสิทธิ์ดาวน์โหลดใบเสร็จของผู้อื่น', 'danger')
        return redirect(url_for('customer.orders'))

    payment = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,)).fetchone()

    # ตรวจสอบเงื่อนไข: ชำระเงินต้องได้รับอนุมัติแล้วเท่านั้น
    if not payment or payment['status'] != 'approved':
        conn.close()
        flash('ใบเสร็จจะออกได้ต่อเมื่อการชำระเงินได้รับการตรวจสอบและอนุมัติแล้วเท่านั้น', 'warning')
        return redirect(url_for('customer.order_detail', order_id=order_id))

    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()

    # ดึงหรือสร้างเลขที่ใบเสร็จ
    receipt_row = conn.execute("SELECT * FROM receipts WHERE order_id = ?", (order_id,)).fetchone()
    if not receipt_row:
        receipt_number = f"REC-{order['order_number'].replace('ORD-', '')}"
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO receipts (receipt_number, order_id) VALUES (?, ?)", (receipt_number, order_id))
        conn.commit()
    else:
        receipt_number = receipt_row['receipt_number']

    conn.close()

    # สร้างไฟล์ PDF ด้วย ReportLab
    pdf_buffer = generate_receipt_pdf(order, items, receipt_number, payment)

    filename = f"Receipt_{order['order_number']}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


# ================== ระบบแจ้งปัญหาและติดต่อร้าน (Customer Support Tickets) ==================

@customer_bp.route('/tickets', methods=['GET', 'POST'])
@login_required
def tickets():
    """หน้าแจ้งปัญหาสำหรับลูกค้า: ดูรายการที่ตนเองแจ้ง และส่งเรื่องแจ้งปัญหาใหม่"""
    conn = get_db_connection()

    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        subject = request.form.get('subject', '').strip()
        details = request.form.get('details', '').strip()
        order_number = request.form.get('order_number', '').strip()
        contact_info = request.form.get('contact_info', '').strip()

        if not category or not subject or not details:
            flash('กรุณากรอกหมวดหมู่ปัญหา หัวข้อ และรายละเอียดให้ครบถ้วน', 'danger')
            conn.close()
            return redirect(url_for('customer.tickets'))

        # ตรวจสอบ order_id หากมีการระบุเลขที่คำสั่งซื้อ
        order_id = None
        if order_number:
            ord_row = conn.execute("SELECT id FROM orders WHERE order_number = ? AND user_id = ?", (order_number, session['user_id'])).fetchone()
            if ord_row:
                order_id = ord_row['id']

        date_str = datetime.now().strftime('%Y%m%d')
        count_today = conn.execute("SELECT COUNT(*) FROM support_tickets WHERE ticket_code LIKE ?", (f"TCK-{date_str}-%",)).fetchone()[0] + 1
        ticket_code = f"TCK-{date_str}-{count_today:04d}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO support_tickets (ticket_code, user_id, category, subject, details, order_id, contact_info, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'รอตรวจสอบ')
        """, (ticket_code, session['user_id'], category, subject, details, order_id, contact_info))
        conn.commit()
        conn.close()

        flash(f'ส่งเรื่องแจ้งปัญหาเรียบร้อยแล้ว เลขที่อ้างอิงของคุณคือ {ticket_code}', 'success')
        return redirect(url_for('customer.tickets'))

    # ดึงเฉพาะเรื่องที่ผู้ใช้นี้แจ้งเท่านั้น
    my_tickets = conn.execute("""
        SELECT t.*, o.order_number
        FROM support_tickets t
        LEFT JOIN orders o ON t.order_id = o.id
        WHERE t.user_id = ?
        ORDER BY t.id DESC
    """, (session['user_id'],)).fetchall()

    # ดึงคำสั่งซื้อของผู้ใช้เพื่อให้เลือกใน Dropdown
    my_orders = conn.execute("SELECT id, order_number FROM orders WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()

    return render_template('customer_tickets.html', tickets=my_tickets, orders=my_orders)


@customer_bp.route('/ticket/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    """ดูรายละเอียดเรื่องแจ้งปัญหา ตรวจสอบสิทธิ์เฉพาะเจ้าของเรื่อง"""
    conn = get_db_connection()
    ticket = conn.execute("""
        SELECT t.*, o.order_number, u.name as admin_name
        FROM support_tickets t
        LEFT JOIN orders o ON t.order_id = o.id
        LEFT JOIN users u ON t.replied_by = u.id
        WHERE t.id = ?
    """, (ticket_id,)).fetchone()
    conn.close()

    if not ticket or ticket['user_id'] != session['user_id']:
        flash('ไม่พบเรื่องแจ้งปัญหาหรือไม่มีสิทธิ์เข้าถึง', 'danger')
        return redirect(url_for('customer.tickets'))

    return render_template('customer_ticket_detail.html', ticket=ticket)

