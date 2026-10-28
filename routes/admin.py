"""
routes/admin.py
ระบบจัดการหลังบ้านสำหรับผู้ดูแลระบบ (Admin)
Dashboard สถิติ, จัดการสินค้า, ตรวจสอบการชำระเงิน, จัดการคำสั่งซื้อ, และรายงานสรุป
"""

import os
import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from database import get_db_connection, log_order_status, archive_old_completed_orders
from routes.auth import admin_required
from routes.receipt import generate_receipt_pdf
from routes.helpers import allowed_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCT_UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'ไฟล์ที่ผู้ใช้อัปโหลด', 'products')


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    แดชบอร์ดสรุปสถิติสำคัญและการวิเคราะห์ยอดขายจากข้อมูลจริงใน SQLite เท่านั้น
    - รองรับตัวกรอง: รายวัน, รายเดือน, รายปี, ทั้งหมด, หรือช่วงวันที่กำหนดเอง
    - คำนวณยอดขายจริงเฉพาะคำสั่งซื้อที่ชำระเงินแล้ว ไม่รวมคำสั่งซื้อที่ยกเลิก
    - คำนวณจำนวนคันที่ขายได้จาก order_items ไม่ใช่จำนวนคำสั่งซื้อ
    - ระบบแนะนำการเติมสต็อกอ้างอิงอัตราการขายจริง (30/60/90 วัน)
    - ปราศจากข้อมูลจำลองหรือข้อมูลปลอม
    """
    conn = get_db_connection()

    # รับตัวกรองช่วงเวลา (period: 'all', 'today', 'month', 'year', 'custom')
    period = request.args.get('period', 'all').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # สร้างเงื่อนไข SQL สำหรับช่วงเวลา
    date_clause = ""
    date_params = []

    if period == 'today':
        date_clause = " AND DATE(o.created_at) = DATE('now', 'localtime')"
    elif period == 'month':
        date_clause = " AND strftime('%Y-%m', o.created_at) = strftime('%Y-%m', 'now', 'localtime')"
    elif period == 'year':
        date_clause = " AND strftime('%Y', o.created_at) = strftime('%Y', 'now', 'localtime')"
    elif period == 'custom':
        if start_date:
            date_clause += " AND DATE(o.created_at) >= DATE(?)"
            date_params.append(start_date)
        if end_date:
            date_clause += " AND DATE(o.created_at) <= DATE(?)"
            date_params.append(end_date)
    else:
        period = 'all'

    # 1. ข้อมูลสต็อก: แยกความหมายชัดเจนระหว่าง "จำนวนรุ่นสินค้า" และ "จำนวนคันรวมในสต็อกจริง"
    total_models = conn.execute("SELECT COUNT(DISTINCT model) FROM products").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_stock_units = conn.execute("SELECT COALESCE(SUM(stock), 0) FROM products").fetchone()[0]

    # 2. ยอดขายจริงที่ได้รับชำระเงินแล้ว (Paid Revenue) ในช่วงเวลาที่เลือก
    paid_sales_query = f"""
        SELECT COALESCE(SUM(o.total_amount), 0)
        FROM orders o
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        {date_clause}
    """
    total_sales = float(conn.execute(paid_sales_query, date_params).fetchone()[0])

    # 3. ยอดสั่งซื้อทั้งหมดรวมคำสั่งซื้อที่ยังไม่ชำระ (Total Ordered Amount - ไม่รวมยกเลิก)
    total_ordered_query = f"""
        SELECT COALESCE(SUM(o.total_amount), 0)
        FROM orders o
        WHERE o.status != 'ยกเลิก'
        {date_clause}
    """
    total_ordered_amount = float(conn.execute(total_ordered_query, date_params).fetchone()[0])

    # 4. จำนวนคันที่ขายได้จริง (Units Sold) คำนวณจาก order_items
    units_sold_query = f"""
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        {date_clause}
    """
    total_units_sold = int(conn.execute(units_sold_query, date_params).fetchone()[0])

    # 5. จำนวนคำสั่งซื้อที่ชำระเงินแล้ว และจำนวนคำสั่งซื้อทั้งหมดในงวด
    paid_orders_query = f"""
        SELECT COUNT(DISTINCT o.id)
        FROM orders o
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        {date_clause}
    """
    paid_orders_count = int(conn.execute(paid_orders_query, date_params).fetchone()[0])

    period_orders_query = f"""
        SELECT COUNT(DISTINCT o.id)
        FROM orders o
        WHERE o.status != 'ยกเลิก'
        {date_clause}
    """
    total_period_orders = int(conn.execute(period_orders_query, date_params).fetchone()[0])

    # 6. ยอดขายแยกตามรุ่นรถ (Revenue and units by model จาก order_items.price ในประวัติคำสั่งซื้อ)
    sales_by_model_query = f"""
        SELECT oi.product_name, p.brand, p.category, p.stock as current_stock,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        {date_clause}
        GROUP BY oi.product_name
        ORDER BY total_revenue DESC, units_sold DESC
    """
    sales_by_model = conn.execute(sales_by_model_query, date_params).fetchall()

    top_selling_models = sales_by_model[:5]
    low_selling_models = [m for m in sales_by_model if m['units_sold'] > 0][-5:] if len(sales_by_model) > 1 else []

    # 7. สินค้าที่ไม่มีการขายในช่วงเวลาที่เลือก (Zero-Sales Models)
    sold_names = [m['product_name'] for m in sales_by_model]
    if sold_names:
        placeholders = ','.join(['?'] * len(sold_names))
        zero_sales_items = conn.execute(f"""
            SELECT code, brand, model, price, stock, category
            FROM products
            WHERE model NOT IN ({placeholders}) AND status != 'discontinued'
            ORDER BY stock DESC
        """, sold_names).fetchall()
    else:
        zero_sales_items = conn.execute("""
            SELECT code, brand, model, price, stock, category
            FROM products
            WHERE status != 'discontinued'
            ORDER BY stock DESC
        """).fetchall()

    # 8. สินค้าใกล้หมดและหมดสต็อก
    low_stock_items = conn.execute("""
        SELECT * FROM products 
        WHERE stock < 3 AND status != 'discontinued'
        ORDER BY stock ASC
    """).fetchall()
    low_stock_count = len(low_stock_items)

    out_of_stock_items = conn.execute("""
        SELECT * FROM products 
        WHERE stock = 0 AND status != 'discontinued'
        ORDER BY model ASC
    """).fetchall()

    # 9. จำนวนสมาชิกและคำสั่งซื้อสถานะต่างๆ
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'").fetchone()[0]
    pending_payments = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'รอตรวจสอบการชำระเงิน'").fetchone()[0]
    new_orders_count = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'รอชำระเงิน'").fetchone()[0]
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    # คำสั่งซื้อล่าสุด 6 รายการ
    recent_orders = conn.execute("""
        SELECT o.*, 
               (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
               (SELECT status FROM payments WHERE order_id = o.id) as payment_status
        FROM orders o
        WHERE o.is_archived = 0
        ORDER BY o.id DESC
        LIMIT 6
    """).fetchall()

    # 10. สรุปยอดขายย้อนหลัง 7 วัน สำหรับกราฟ Pure CSS Bar Chart (NO JavaScript)
    today = datetime.now().date()
    daily_sales = []
    thai_days_short = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสฯ', 'ศุกร์', 'เสาร์', 'อาทิตย์']
    max_daily_amt = 1.0

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        weekday_name = thai_days_short[day.weekday()]
        label = f"{weekday_name} ({day.strftime('%d/%m')})"
        amt_row = conn.execute("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM orders
            WHERE DATE(created_at) = ? AND status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        """, (day_str,)).fetchone()
        amt = float(amt_row[0])
        if amt > max_daily_amt:
            max_daily_amt = amt
        daily_sales.append({
            'date': day_str,
            'label': label,
            'amount': amt
        })

    # คำนวณความสูงเปอร์เซ็นต์สำหรับ Pure CSS Bar
    for d in daily_sales:
        d['height_percent'] = round((d['amount'] / max_daily_amt) * 100, 1) if max_daily_amt > 0 else 0

    sales_7days_total = sum(d['amount'] for d in daily_sales)

    # 11. ระบบวิเคราะห์และแนะนำการเติมสต็อก (Stock Replenishment Analysis) จากยอดขายจริง
    # ตรวจสอบยอดขายรวมสะสมทั้งร้านก่อน
    cumulative_paid_orders = conn.execute("""
        SELECT COUNT(*) FROM orders WHERE status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """).fetchone()[0]
    is_data_insufficient = (cumulative_paid_orders < 2)

    all_active_products = conn.execute("""
        SELECT id, code, brand, model, price, stock, category
        FROM products
        WHERE status != 'discontinued'
        ORDER BY stock ASC
    """).fetchall()

    replenishment_recommendations = []
    for p in all_active_products:
        p_name = p['model']
        # คำนวณยอดขายย้อนหลัง 30, 60, 90 วัน
        sales_30 = conn.execute("""
            SELECT COALESCE(SUM(oi.quantity), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE oi.product_id = ? AND o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
              AND DATE(o.created_at) >= DATE('now', '-30 days')
        """, (p['id'],)).fetchone()[0]

        sales_60 = conn.execute("""
            SELECT COALESCE(SUM(oi.quantity), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE oi.product_id = ? AND o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
              AND DATE(o.created_at) >= DATE('now', '-60 days')
        """, (p['id'],)).fetchone()[0]

        sales_90 = conn.execute("""
            SELECT COALESCE(SUM(oi.quantity), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE oi.product_id = ? AND o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
              AND DATE(o.created_at) >= DATE('now', '-90 days')
        """, (p['id'],)).fetchone()[0]

        # อัตราขายเฉลี่ยต่อเดือน (30 วัน)
        monthly_sales_rate = sales_30

        # วิเคราะห์สถานะและคำแนะนำ
        current_stock = p['stock']
        if current_stock == 0:
            rec_level = 'urgent'
            rec_badge = 'สินค้าหมดสต็อก'
            rec_reason = f'สต็อกเหลือ 0 คัน (ยอดขาย 30 วัน: {sales_30} คัน) ควรพิจารณาเติมสต็อกเพื่อไม่ให้เสียโอกาสการขาย'
        elif current_stock <= 2 and sales_30 >= 2:
            rec_level = 'urgent'
            rec_badge = 'ขายดีสต็อกต่ำ'
            rec_reason = f'ขายได้ {sales_30} คันใน 30 วัน แต่เหลือสต็อกเพียง {current_stock} คัน แนะนำพิจารณาเติมสต็อกด่วน'
        elif current_stock <= 2:
            rec_level = 'warning'
            rec_badge = 'สต็อกใกล้หมด'
            rec_reason = f'สต็อกคงเหลือต่ำ ({current_stock} คัน) แม้ยอดขาย 30 วันมี {sales_30} คัน แนะนำวางแผนเติมสต็อกสำรอง'
        elif sales_60 == 0 and current_stock >= 5:
            rec_level = 'slow'
            rec_badge = 'ขายช้าสต็อกหนาแน่น'
            rec_reason = f'ไม่มีคำสั่งซื้อใน 60 วันที่ผ่านมา และมีสต็อกอยู่ถึง {current_stock} คัน ควรชะลอการสั่งเติม'
        else:
            rec_level = 'normal'
            rec_badge = 'สต็อกปกติ'
            rec_reason = f'สต็อกคงเหลือ {current_stock} คัน สอดคล้องกับอัตราการขายเฉลี่ย'

        replenishment_recommendations.append({
            'product': p,
            'sales_30': sales_30,
            'sales_60': sales_60,
            'sales_90': sales_90,
            'monthly_rate': monthly_sales_rate,
            'current_stock': current_stock,
            'rec_level': rec_level,
            'rec_badge': rec_badge,
            'rec_reason': rec_reason
        })

    # เรียงลำดับคำแนะนำ: urgent มาก่อน ตามด้วย warning, slow, normal
    level_order = {'urgent': 1, 'warning': 2, 'slow': 3, 'normal': 4}
    replenishment_recommendations.sort(key=lambda x: (level_order.get(x['rec_level'], 99), x['current_stock']))

    # ข้อมูลเวลาเปิดทำการ
    now = datetime.now()
    is_store_open = (now.weekday() == 2 and 9 <= now.hour < 18)
    thai_months = ['', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
    current_date_thai = f"{now.day} {thai_months[now.month]} {now.year + 543}"
    current_time_str = now.strftime('%H:%M น.')

    conn.close()

    return render_template('admin/dashboard.html',
                           period=period,
                           start_date=start_date,
                           end_date=end_date,
                           total_products=total_products,
                           total_models=total_models,
                           total_stock_units=total_stock_units,
                           total_sales=total_sales,
                           total_ordered_amount=total_ordered_amount,
                           total_units_sold=total_units_sold,
                           paid_orders_count=paid_orders_count,
                           total_period_orders=total_period_orders,
                           sales_by_model=sales_by_model,
                           top_selling_models=top_selling_models,
                           low_selling_models=low_selling_models,
                           zero_sales_items=zero_sales_items,
                           low_stock_items=low_stock_items,
                           low_stock_count=low_stock_count,
                           out_of_stock_items=out_of_stock_items,
                           total_orders=total_orders,
                           pending_payments=pending_payments,
                           new_orders_count=new_orders_count,
                           total_users=total_users,
                           recent_orders=recent_orders,
                           daily_sales=daily_sales,
                           sales_7days_total=sales_7days_total,
                           replenishment_recommendations=replenishment_recommendations,
                           is_data_insufficient=is_data_insufficient,
                           is_store_open=is_store_open,
                           current_date_thai=current_date_thai,
                           current_time_str=current_time_str)


# ================== จัดการสินค้า (Products CRUD) ==================

@admin_bp.route('/products')
@admin_required
def products():
    """หน้ารายการสินค้าทั้งหมดในระบบหลังบ้าน"""
    conn = get_db_connection()
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if search:
        query += " AND (model LIKE ? OR code LIKE ? OR brand LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"
    all_products = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('admin/products.html', products=all_products, search=search, category=category)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def product_add():
    """เพิ่มสินค้าใหม่เข้าระบบ (ตรวจสอบความจุ <= 160 cc)"""
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        brand = request.form.get('brand', '').strip()
        model = request.form.get('model', '').strip()
        model_year = request.form.get('model_year', '').strip() or 'ไม่ทราบปี'
        engine_cc = request.form.get('engine_cc', type=int)
        category = request.form.get('category', '').strip()
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', default=0, type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'available')

        # การตรวจสอบความถูกต้องฝั่ง Server
        if not code or not brand or not model or engine_cc is None or price is None:
            flash('กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน', 'danger')
            return render_template('admin/product_form.html', action='add')

        # กฎเหล็ก: ความจุเครื่องยนต์ห้ามเกิน 160 cc
        if engine_cc > 160 or engine_cc <= 0:
            flash('ระบบจำกัดเฉพาะรถจักรยานยนต์ความจุไม่เกิน 160 cc เท่านั้น', 'danger')
            return render_template('admin/product_form.html', action='add')

        if price < 0 or stock < 0:
            flash('ราคาและจำนวนสต็อกต้องไม่ติดลบ', 'danger')
            return render_template('admin/product_form.html', action='add')

        # จัดการรูปภาพ
        image_url = 'wave110i.svg'  # รูปภาพเริ่มต้น
        if 'image_file' in request.files and request.files['image_file'].filename:
            img = request.files['image_file']
            if allowed_file(img.filename):
                os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)
                ext = img.filename.rsplit('.', 1)[1].lower()
                safe_name = f"prod_{code}_{int(time.time())}.{ext}"
                img.save(os.path.join(PRODUCT_UPLOAD_DIR, safe_name))
                image_url = safe_name

        conn = get_db_connection()
        # ตรวจสอบรหัสสินค้าซ้ำ
        dup = conn.execute("SELECT id FROM products WHERE code = ?", (code,)).fetchone()
        if dup:
            conn.close()
            flash(f'รหัสสินค้า {code} มีอยู่ในระบบแล้ว', 'danger')
            return render_template('admin/product_form.html', action='add')

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (code, brand, model, model_year, engine_cc, category, price, stock, description, image_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, brand, model, model_year, engine_cc, category, price, stock, description, image_url, status))
        conn.commit()
        conn.close()

        flash(f'เพิ่มรถรุ่น {model} เข้าระบบเรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', action='add')


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    """แก้ไขข้อมูลสินค้าเดิม"""
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        conn.close()
        flash('ไม่พบสินค้าที่ต้องการแก้ไข', 'danger')
        return redirect(url_for('admin.products'))

    if request.method == 'POST':
        brand = request.form.get('brand', '').strip()
        model = request.form.get('model', '').strip()
        model_year = request.form.get('model_year', '').strip() or 'ไม่ทราบปี'
        engine_cc = request.form.get('engine_cc', type=int)
        category = request.form.get('category', '').strip()
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'available')

        if not brand or not model or engine_cc is None or price is None:
            conn.close()
            flash('กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน', 'danger')
            return render_template('admin/product_form.html', action='edit', product=product)

        if engine_cc > 160 or engine_cc <= 0:
            conn.close()
            flash('ระบบจำกัดเฉพาะรถจักรยานยนต์ความจุไม่เกิน 160 cc เท่านั้น', 'danger')
            return render_template('admin/product_form.html', action='edit', product=product)

        if price < 0 or stock < 0:
            conn.close()
            flash('ราคาและจำนวนสต็อกต้องไม่ติดลบ', 'danger')
            return render_template('admin/product_form.html', action='edit', product=product)

        image_url = product['image_url']
        if 'image_file' in request.files and request.files['image_file'].filename:
            img = request.files['image_file']
            if allowed_file(img.filename):
                os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)
                ext = img.filename.rsplit('.', 1)[1].lower()
                safe_name = f"prod_{product['code']}_{int(time.time())}.{ext}"
                img.save(os.path.join(PRODUCT_UPLOAD_DIR, safe_name))
                image_url = safe_name

        cursor = conn.cursor()
        old_stock = product['stock']
        if stock != old_stock:
            cursor.execute("""
                INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, old_stock, stock, stock - old_stock, 'แก้ไขข้อมูลและปรับสต็อกผ่านแบบฟอร์มสินค้า', session['user_id'], session.get('user_name', 'Admin')))

        cursor.execute("""
            UPDATE products 
            SET brand = ?, model = ?, model_year = ?, engine_cc = ?, category = ?, 
                price = ?, stock = ?, description = ?, image_url = ?, status = ?
            WHERE id = ?
        """, (brand, model, model_year, engine_cc, category, price, stock, description, image_url, status, product_id))
        conn.commit()
        conn.close()

        flash(f'แก้ไขข้อมูล {model} เรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin.products'))

    conn.close()
    return render_template('admin/product_form.html', action='edit', product=product)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def product_delete(product_id):
    """ลบสินค้า โดยตรวจสอบประวัติคำสั่งซื้อเพื่อป้องกันความเสียหายของข้อมูล"""
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        conn.close()
        flash('ไม่พบสินค้าที่ต้องการลบ', 'danger')
        return redirect(url_for('admin.products'))

    # ตรวจสอบว่าสินค้านี้เคยมีลูกค้าสั่งซื้อหรือไม่
    order_ref = conn.execute("SELECT COUNT(*) FROM order_items WHERE product_id = ?", (product_id,)).fetchone()[0]

    cursor = conn.cursor()
    if order_ref > 0:
        # หากมีประวัติคำสั่งซื้อ ให้เปลี่ยนสถานะเป็นเลิกจำหน่าย (Soft Delete) เพื่อรักษาประวัติคำสั่งซื้อ
        cursor.execute("UPDATE products SET status = 'discontinued', stock = 0 WHERE id = ?", (product_id,))
        cursor.execute("""
            INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
            VALUES (?, ?, 0, ?, 'ปิดการขาย (เลิกจำหน่าย) เนื่องจากมีประวัติคำสั่งซื้อ', ?, ?)
        """, (product_id, product['stock'], -product['stock'], session['user_id'], session.get('user_name', 'Admin')))
        conn.commit()
        conn.close()
        flash(f'สินค้านี้มีประวัติคำสั่งซื้อแล้ว ระบบได้ทำการ "ปิดการขาย (เลิกจำหน่าย)" แทนการลบเพื่อรักษาความถูกต้องของข้อมูลประวัติคำสั่งซื้อ', 'warning')
    else:
        # หากยังไม่มีประวัติ อนุญาตให้ลบได้จริง
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        flash(f'ลบสินค้า {product["model"]} ออกจากระบบเรียบร้อยแล้ว', 'success')

    return redirect(url_for('admin.products'))


@admin_bp.route('/products/stock/<int:product_id>', methods=['POST'])
@admin_required
def product_stock_update(product_id):
    """ปรับปรุงจำนวนสต็อกสินค้าโดยตรง พร้อมบันทึกประวัติการปรับสต็อก (Audit Log)"""
    new_stock = request.form.get('stock', type=int)
    reason = request.form.get('reason', '').strip() or 'ปรับปรุงสต็อกโดยผู้ดูแลระบบ'

    if new_stock is None or new_stock < 0:
        flash('จำนวนสต็อกต้องเป็นตัวเลขที่ไม่ติดลบ', 'danger')
        return redirect(url_for('admin.products'))

    conn = get_db_connection()
    cursor = conn.cursor()
    product = cursor.execute("SELECT id, model, stock FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        flash('ไม่พบสินค้าที่ต้องการปรับปรุงสต็อก', 'danger')
        return redirect(url_for('admin.products'))

    old_stock = product['stock']
    change_qty = new_stock - old_stock

    cursor.execute("""
        UPDATE products 
        SET stock = ?,
            status = CASE WHEN ? = 0 THEN 'out_of_stock' ELSE (CASE WHEN status = 'out_of_stock' THEN 'available' ELSE status END) END
        WHERE id = ?
    """, (new_stock, new_stock, product_id))

    cursor.execute("""
        INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (product_id, old_stock, new_stock, change_qty, reason, session.get('user_id'), session.get('user_name', 'Admin')))

    conn.commit()
    conn.close()

    flash(f'ปรับปรุงสต็อก {product["model"]} จาก {old_stock} เป็น {new_stock} คัน เรียบร้อยแล้ว (เหตุผล: {reason})', 'success')
    return redirect(url_for('admin.products'))


# ================== จัดการคำสั่งซื้อ (Orders Management) ==================

@admin_bp.route('/orders')
@admin_required
def orders():
    """แสดงรายการคำสั่งซื้อทั้งหมด พร้อมแท็บแยกคลังประวัติ (Archived)"""
    conn = get_db_connection()
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    show_archived = request.args.get('archived', '0') == '1'

    query = """
        SELECT o.*, 
               (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
               (SELECT status FROM payments WHERE order_id = o.id) as payment_status
        FROM orders o
        WHERE 1=1
    """
    params = []
    if show_archived:
        query += " AND o.is_archived = 1"
    else:
        query += " AND o.is_archived = 0"

    if status_filter:
        query += " AND o.status = ?"
        params.append(status_filter)
    if search:
        query += " AND (o.order_number LIKE ? OR o.customer_name LIKE ? OR o.customer_phone LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY o.id DESC"
    all_orders = conn.execute(query, params).fetchall()

    archived_count = conn.execute("SELECT COUNT(*) FROM orders WHERE is_archived = 1").fetchone()[0]
    conn.close()

    return render_template('admin/orders.html', orders=all_orders, current_status=status_filter, search=search, show_archived=show_archived, archived_count=archived_count)


@admin_bp.route('/order/<int:order_id>')
@admin_required
def order_detail(order_id):
    """ดูรายละเอียดคำสั่งซื้อของลูกค้าในมุมมองผู้ดูแลระบบ"""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อ', 'danger')
        return redirect(url_for('admin.orders'))

    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    payment = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,)).fetchone()
    history = conn.execute("SELECT * FROM order_status_history WHERE order_id = ? ORDER BY id ASC", (order_id,)).fetchall()
    receipt = conn.execute("SELECT * FROM receipts WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()

    return render_template('admin/order_detail.html', 
                           order=order, 
                           items=items, 
                           payment=payment, 
                           history=history,
                           status_history=history,
                           receipt=receipt)


@admin_bp.route('/order/<int:order_id>/status', methods=['POST'])
@admin_required
def order_update_status(order_id):
    """เปลี่ยนสถานะคำสั่งซื้อ พร้อมบันทึกประวัติการเปลี่ยนสถานะ และคืนสต็อกเพียงครั้งเดียวหากยกเลิก"""
    new_status = request.form.get('status', '').strip()
    notes = request.form.get('notes', '').strip()

    valid_statuses = ['รอชำระเงิน', 'รอตรวจสอบการชำระเงิน', 'ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว', 'ยกเลิก']
    if new_status not in valid_statuses:
        flash('สถานะไม่ถูกต้อง', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อ', 'danger')
        return redirect(url_for('admin.orders'))

    old_status = order['status']
    cursor = conn.cursor()

    try:
        # หากเปลี่ยนเป็นยกเลิก และยังไม่เคยคืนสต็อก ให้คืนสต็อกเพียงครั้งเดียว
        if new_status == 'ยกเลิก' and not order['is_restocked']:
            items = cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
            for it in items:
                cur_p = cursor.execute("SELECT stock FROM products WHERE id = ?", (it['product_id'],)).fetchone()
                if cur_p:
                    old_s = cur_p['stock']
                    new_s = old_s + it['quantity']
                    cursor.execute("""
                        UPDATE products 
                        SET stock = ?,
                            status = CASE WHEN status = 'out_of_stock' THEN 'available' ELSE status END
                        WHERE id = ?
                    """, (new_s, it['product_id']))
                    cursor.execute("""
                        INSERT INTO stock_adjustments (product_id, old_stock, new_stock, change_qty, reason, admin_id, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (it['product_id'], old_s, new_s, it['quantity'], f"คืนสต็อกจากการยกเลิกคำสั่งซื้อ {order['order_number']}", session['user_id'], session.get('user_name', 'Admin')))
            cursor.execute("UPDATE orders SET is_restocked = 1 WHERE id = ?", (order_id,))

        cursor.execute("UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, order_id))
        
        status_note = notes or f"แอดมินเปลี่ยนสถานะจาก '{old_status}' เป็น '{new_status}'"
        log_order_status(conn, order_id, new_status, status_note, session.get('user_name', 'Admin'))

        # หากสถานะเปลี่ยนเป็นเสร็จสิ้น ให้จัดเก็บประวัติอัตโนมัติคงเหลือ 3 ออเดอร์ล่าสุด
        if new_status in ('ชำระเงินแล้ว', 'จัดส่งแล้ว'):
            archive_old_completed_orders(conn)

        conn.commit()
        flash(f'อัปเดตสถานะเป็น "{new_status}" เรียบร้อยแล้ว', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'เกิดข้อผิดพลาดในการเปลี่ยนสถานะ: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/order/<int:order_id>/shipping', methods=['POST'])
@admin_required
def order_update_shipping(order_id):
    """บันทึกหรือปรับปรุงค่าจัดส่งจริงตามที่ผู้ดูแลระบบประเมิน"""
    shipping_fee = request.form.get('shipping_fee', type=float)
    if shipping_fee is None or shipping_fee < 0:
        flash('ค่าจัดส่งต้องเป็นตัวเลขที่ไม่ติดลบ', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        flash('ไม่พบคำสั่งซื้อ', 'danger')
        return redirect(url_for('admin.orders'))

    cursor = conn.cursor()
    # คำนวณยอดรวมสุทธิใหม่ (subtotal รวม VAT แล้ว ไม่นำ VAT มาบวกซ้ำ)
    subtotal = float(order['subtotal'])
    discount = float(order['discount'])
    new_total = round(subtotal - discount + shipping_fee, 2)

    cursor.execute("""
        UPDATE orders 
        SET shipping_fee = ?,
            is_shipping_estimated = 0,
            total_amount = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (shipping_fee, new_total, order_id))

    # หากมีการสร้าง payment record รออยู่แล้ว ให้อัปเดตยอด amount ด้วย
    cursor.execute("UPDATE payments SET amount = ? WHERE order_id = ? AND status = 'pending'", (new_total, order_id))

    log_order_status(conn, order_id, order['status'], f"แอดมินยืนยันค่าจัดส่งเป็น ฿{shipping_fee:,.2f} ยอดสุทธิปรับเป็น ฿{new_total:,.2f}", session.get('user_name', 'Admin'))
    conn.commit()
    conn.close()

    flash(f'ปรับปรุงค่าจัดส่งเป็น ฿{shipping_fee:,.2f} และคำนวณยอดสุทธิใหม่เรียบร้อยแล้ว', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ================== ตรวจสอบการชำระเงิน (Payments Verification) ==================

@admin_bp.route('/payments')
@admin_required
def payments():
    """หน้ารายการหลักฐานการชำระเงินทั้งหมดเพื่อรอตรวจสอบ"""
    conn = get_db_connection()
    show_archived = request.args.get('archived', '0') == '1'

    query = """
        SELECT p.*, o.order_number, o.customer_name, o.customer_phone, o.status as order_status,
               u.name as verified_by_name
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        LEFT JOIN users u ON p.verified_by = u.id
        WHERE 1=1
    """
    if show_archived:
        query += " AND o.is_archived = 1"
    else:
        query += " AND o.is_archived = 0"

    query += " ORDER BY CASE WHEN p.status = 'pending' THEN 0 ELSE 1 END, p.id DESC"
    payments_list = conn.execute(query).fetchall()
    conn.close()

    return render_template('admin/payments.html', payments=payments_list, show_archived=show_archived)


@admin_bp.route('/payment/<int:order_id>/verify', methods=['POST'])
@admin_required
def payment_verify(order_id):
    """อนุมัติหรือปฏิเสธสลิปการชำระเงิน ป้องกันการอนุมัติซ้ำ และสร้างใบเสร็จอัตโนมัติ"""
    action = request.form.get('action')  # 'approve' หรือ 'reject'
    reject_reason = request.form.get('reject_reason', '').strip()

    conn = get_db_connection()
    payment = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,)).fetchone()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    if not payment or not order:
        conn.close()
        flash('ไม่พบข้อมูลการชำระเงิน', 'danger')
        return redirect(url_for('admin.payments'))

    cursor = conn.cursor()

    if action == 'approve':
        # ป้องกันการอนุมัติซ้ำ
        if payment['status'] == 'approved':
            conn.close()
            flash('คำสั่งซื้อนี้ได้รับการอนุมัติการชำระเงินไปแล้ว ไม่สามารถอนุมัติซ้ำได้', 'warning')
            return redirect(url_for('admin.payments'))

        # 1. อัปเดตสถานะการชำระเงินเป็น approved
        cursor.execute("""
            UPDATE payments 
            SET status = 'approved', verified_by = ?, verified_at = CURRENT_TIMESTAMP, reject_reason = NULL
            WHERE order_id = ?
        """, (session['user_id'], order_id))

        # 2. ปรับสถานะคำสั่งซื้อเป็น "ชำระเงินแล้ว"
        cursor.execute("""
            UPDATE orders 
            SET status = 'ชำระเงินแล้ว', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (order_id,))

        # 3. บันทึกเลขที่ใบเสร็จในตาราง receipts (ถ้ายังไม่มี)
        receipt_number = f"REC-{order['order_number'].replace('ORD-', '')}"
        cursor.execute("INSERT OR IGNORE INTO receipts (receipt_number, order_id) VALUES (?, ?)", (receipt_number, order_id))

        # 4. บันทึกประวัติสถานะ
        log_order_status(conn, order_id, 'ชำระเงินแล้ว', 'เจ้าหน้าที่ตรวจสอบยอดเงินถูกต้องและอนุมัติการชำระเงินแล้ว ออกใบเสร็จเรียบร้อย', session.get('user_name', 'Admin'))

        # 5. จัดเก็บประวัติคำสั่งซื้ออัตโนมัติคงเหลือ 3 ออเดอร์ล่าสุด
        archive_old_completed_orders(conn)

        conn.commit()
        conn.close()
        flash(f'อนุมัติการชำระเงินคำสั่งซื้อ {order["order_number"]} สำเร็จ และเปิดให้ดาวน์โหลดใบเสร็จได้แล้ว', 'success')

    elif action == 'reject':
        if not reject_reason:
            conn.close()
            flash('กรุณาระบุเหตุผลการปฏิเสธเพื่อให้ลูกค้าทราบและดำเนินการใหม่', 'danger')
            return redirect(url_for('admin.payments'))

        cursor.execute("""
            UPDATE payments 
            SET status = 'rejected', reject_reason = ?, verified_by = ?, verified_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (reject_reason, session['user_id'], order_id))

        # ปรับสถานะคำสั่งซื้อกลับเป็น "รอชำระเงิน"
        cursor.execute("""
            UPDATE orders 
            SET status = 'รอชำระเงิน', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (order_id,))

        log_order_status(conn, order_id, 'รอชำระเงิน', f"ปฏิเสธสลิปการชำระเงิน: {reject_reason}", session.get('user_name', 'Admin'))

        conn.commit()
        conn.close()
        flash(f'ปฏิเสธสลิปคำสั่งซื้อ {order["order_number"]} เรียบร้อยแล้ว (เหตุผล: {reject_reason})', 'info')

    else:
        conn.close()
        flash('คำสั่งไม่ถูกต้อง', 'danger')

    return redirect(url_for('admin.payments'))


# ================== รายงานสรุป (Reports) ==================

@admin_bp.route('/reports')
@admin_required
def reports():
    """หน้ารายงานสรุปยอดขาย คำสั่งซื้อ สถิติรุ่นรถยอดนิยม และสถานะสต็อกสินค้าคงเหลือ"""
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    conn = get_db_connection()

    # 1. ข้อมูลสต็อก: แยกชัดเจนระหว่างจำนวนรุ่น (Unique Models) และจำนวนคันรวมในสต็อกจริง (Total Stock Units)
    total_models = conn.execute("SELECT COUNT(DISTINCT model) FROM products").fetchone()[0]
    total_stock_units = conn.execute("SELECT COALESCE(SUM(stock), 0) FROM products").fetchone()[0]

    # รายงานมูลค่าสินค้าคงคลังรวม
    inventory = conn.execute("""
        SELECT id, code, brand, model, engine_cc, category, price, stock, (price * stock) as stock_value, status
        FROM products
        ORDER BY stock ASC, brand ASC
    """).fetchall()
    total_inventory_value = sum(item['stock_value'] for item in inventory)

    # 2. ยอดขายสะสมทั้งหมดตั้งแต่เปิดร้าน (Cumulative Revenue) - นับเฉพาะสถานะชำระเงินสำเร็จ
    cumulative_row = conn.execute("""
        SELECT COALESCE(SUM(total_amount), 0) as total_revenue,
               COUNT(DISTINCT id) as total_orders
        FROM orders
        WHERE status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """).fetchone()
    cumulative_revenue = float(cumulative_row['total_revenue'])
    cumulative_orders = int(cumulative_row['total_orders'])

    # จำนวนคันสะสมทั้งหมดที่ขายได้
    cumulative_units_sold = conn.execute("""
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """).fetchone()[0]

    # 3. ยอดขายตามช่วงเวลาที่กรอง (Period Filtered Sales)
    sales_query = """
        SELECT COUNT(DISTINCT o.id) as order_count, 
               COALESCE(SUM(o.total_amount), 0) as total_sales
        FROM orders o
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    units_query = """
        SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    sales_params = []
    if start_date:
        sales_query += " AND DATE(o.created_at) >= DATE(?)"
        units_query += " AND DATE(o.created_at) >= DATE(?)"
        sales_params.append(start_date)
    if end_date:
        sales_query += " AND DATE(o.created_at) <= DATE(?)"
        units_query += " AND DATE(o.created_at) <= DATE(?)"
        sales_params.append(end_date)

    sales_stat = conn.execute(sales_query, sales_params).fetchone()
    period_units_sold = conn.execute(units_query, sales_params).fetchone()[0]

    # 4. ยอดขายรายวัน (Daily Breakdown) - ย้อนหลังหรือตามช่วงวันที่
    daily_query = """
        SELECT DATE(o.created_at) as sale_date,
               COUNT(DISTINCT o.id) as order_count,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as daily_total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    daily_params = []
    if start_date:
        daily_query += " AND DATE(o.created_at) >= DATE(?)"
        daily_params.append(start_date)
    if end_date:
        daily_query += " AND DATE(o.created_at) <= DATE(?)"
        daily_params.append(end_date)
    daily_query += " GROUP BY DATE(o.created_at) ORDER BY sale_date DESC LIMIT 15"
    daily_breakdown = conn.execute(daily_query, daily_params).fetchall()

    # 5. ยอดขายรายเดือน (Monthly Breakdown)
    monthly_breakdown = conn.execute("""
        SELECT strftime('%Y-%m', o.created_at) as sale_month,
               COUNT(DISTINCT o.id) as order_count,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as monthly_total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        GROUP BY strftime('%Y-%m', o.created_at)
        ORDER BY sale_month DESC
        LIMIT 12
    """).fetchall()

    # 6. ยอดขายรายปี (Yearly Breakdown)
    yearly_breakdown = conn.execute("""
        SELECT strftime('%Y', o.created_at) as sale_year,
               COUNT(DISTINCT o.id) as order_count,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as yearly_total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
        GROUP BY strftime('%Y', o.created_at)
        ORDER BY sale_year DESC
    """).fetchall()

    # 7. สถิติรุ่นรถยอดนิยมและจำนวนคันที่ขายได้ เรียงตามยอดขาย (Best-selling Models)
    model_query = """
        SELECT oi.product_name, p.brand, p.category, p.engine_cc, p.price,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as total_revenue,
               p.stock as current_stock
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    model_params = []
    if start_date:
        model_query += " AND DATE(o.created_at) >= DATE(?)"
        model_params.append(start_date)
    if end_date:
        model_query += " AND DATE(o.created_at) <= DATE(?)"
        model_params.append(end_date)
    model_query += " GROUP BY oi.product_name ORDER BY total_revenue DESC, units_sold DESC"
    best_selling_models = conn.execute(model_query, model_params).fetchall()

    # 7.1 ยอดขายแยกตามประเภทรถ (Category Breakdown) สำหรับ templates/admin/reports.html
    category_query = """
        SELECT COALESCE(p.category, 'ครอบครัว') as category,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as total_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    cat_params = []
    if start_date:
        category_query += " AND DATE(o.created_at) >= DATE(?)"
        cat_params.append(start_date)
    if end_date:
        category_query += " AND DATE(o.created_at) <= DATE(?)"
        cat_params.append(end_date)
    category_query += " GROUP BY p.category ORDER BY total_sales DESC"
    category_sales = conn.execute(category_query, cat_params).fetchall()

    # 7.2 รุ่นรถยอดนิยม (Top Models) สำหรับ templates/admin/reports.html
    top_models_query = """
        SELECT COALESCE(p.model, oi.product_name) as model,
               COALESCE(p.brand, 'Honda') as brand,
               COALESCE(SUM(oi.quantity), 0) as units_sold,
               COALESCE(SUM(oi.subtotal), 0) as total_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    top_params = []
    if start_date:
        top_models_query += " AND DATE(o.created_at) >= DATE(?)"
        top_params.append(start_date)
    if end_date:
        top_models_query += " AND DATE(o.created_at) <= DATE(?)"
        top_params.append(end_date)
    top_models_query += " GROUP BY oi.product_name ORDER BY total_sales DESC, units_sold DESC LIMIT 10"
    top_models = conn.execute(top_models_query, top_params).fetchall()

    # 7.3 คำสั่งซื้อที่เสร็จสิ้นและการออกใบเสร็จ (Completed Orders) สำหรับ templates/admin/reports.html
    completed_orders_query = """
        SELECT o.*
        FROM orders o
        WHERE o.status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')
    """
    comp_params = []
    if start_date:
        completed_orders_query += " AND DATE(o.created_at) >= DATE(?)"
        comp_params.append(start_date)
    if end_date:
        completed_orders_query += " AND DATE(o.created_at) <= DATE(?)"
        comp_params.append(end_date)
    completed_orders_query += " ORDER BY o.id DESC"
    completed_orders = conn.execute(completed_orders_query, comp_params).fetchall()

    # 8. คำสั่งซื้อล่าสุด 10 รายการ และสถานะการชำระเงิน
    recent_orders = conn.execute("""
        SELECT o.*,
               (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
               (SELECT COALESCE(SUM(quantity), 0) FROM order_items WHERE order_id = o.id) as total_units,
               (SELECT status FROM payments WHERE order_id = o.id) as payment_status
        FROM orders o
        ORDER BY o.id DESC
        LIMIT 10
    """).fetchall()

    # 9. รายงานสัดส่วนสถานะคำสั่งซื้อทั้งหมด
    status_stats = conn.execute("""
        SELECT status, COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
        FROM orders
        GROUP BY status
    """).fetchall()

    conn.close()

    return render_template('admin/reports.html',
                           start_date=start_date,
                           end_date=end_date,
                           total_models=total_models,
                           total_stock_units=total_stock_units,
                           total_inventory_value=total_inventory_value,
                           cumulative_revenue=cumulative_revenue,
                           cumulative_orders=cumulative_orders,
                           cumulative_units_sold=cumulative_units_sold,
                           sales_stat=sales_stat,
                           period_units_sold=period_units_sold,
                           daily_breakdown=daily_breakdown,
                           monthly_breakdown=monthly_breakdown,
                           yearly_breakdown=yearly_breakdown,
                           best_selling_models=best_selling_models,
                           top_models=top_models,
                           category_sales=category_sales,
                           completed_orders=completed_orders,
                           recent_orders=recent_orders,
                           status_stats=status_stats,
                           inventory=inventory)


# ================== สมาชิก / ลูกค้า (Customers) ==================

@admin_bp.route('/customers')
@admin_required
def customers():
    """หน้ารายชื่อสมาชิกลูกค้าทั้งหมดในระบบ พร้อมสถานะบัญชีและการจัดการระงับสิทธิ์"""
    conn = get_db_connection()
    customer_list = conn.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.address, u.created_at,
               u.avatar, u.is_banned, u.banned_at, u.banned_reason,
               (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count,
               (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE user_id = u.id AND status IN ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว')) as total_spent
        FROM users u
        WHERE u.role = 'customer'
        ORDER BY u.id DESC
    """).fetchall()
    conn.close()
    return render_template('admin/customers.html', customers=customer_list)


BAN_REASON_CATEGORIES = [
    'ข้อมูลบัญชีไม่ถูกต้องหรือแอบอ้างบุคคลอื่น',
    'ทุจริตหรือส่งหลักฐานการชำระเงินปลอม',
    'ใช้งานระบบในทางที่ผิดหรือพยายามโจมตีระบบ',
    'สแปมหรือสร้างคำสั่งซื้อผิดปกติ',
    'ฝ่าฝืนเงื่อนไขการใช้งาน',
    'อื่น ๆ โดยต้องกรอกรายละเอียดเพิ่มเติม'
]


@admin_bp.route('/customer/<int:user_id>')
@admin_required
def customer_detail(user_id):
    """ดูข้อมูลลูกค้า ประวัติคำสั่งซื้อ และประวัติการระงับบัญชี (Audit Log)"""
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM users WHERE id = ? AND role = 'customer'", (user_id,)).fetchone()
    if not customer:
        conn.close()
        flash('ไม่พบข้อมูลลูกค้าที่ระบุ', 'danger')
        return redirect(url_for('admin.customers'))

    orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    total_spent = sum(o['total_amount'] for o in orders if o['status'] in ('ชำระเงินแล้ว', 'กำลังจัดเตรียมสินค้า', 'จัดส่งแล้ว'))
    ban_logs = conn.execute("""
        SELECT * FROM user_ban_logs 
        WHERE user_id = ? 
        ORDER BY id DESC
    """, (user_id,)).fetchall()
    conn.close()

    return render_template('admin/customer_detail.html', customer=customer, orders=orders, total_spent=total_spent, ban_logs=ban_logs)


@admin_bp.route('/customer/<int:user_id>/ban', methods=['GET', 'POST'])
@admin_required
def customer_ban(user_id):
    """ระงับการใช้งานบัญชีลูกค้า พร้อมเลือก 1 ใน 6 เหตุผลบังคับและบันทึกประวัติการระงับ (Audit Log)"""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        conn.close()
        flash('ไม่พบสมาชิกลูกค้าที่ระบุ', 'danger')
        return redirect(url_for('admin.customers'))

    if user['role'] == 'admin':
        conn.close()
        flash('ไม่อนุญาตให้ระงับการใช้งานบัญชีผู้ดูแลระบบ (Admin)', 'danger')
        return redirect(url_for('admin.customers'))

    if request.method == 'POST':
        reason_category = request.form.get('reason_category', '').strip()
        reason_detail = request.form.get('reason_detail', '').strip()

        if reason_category not in BAN_REASON_CATEGORIES:
            conn.close()
            flash('กรุณาเลือกเหตุผลการระงับบัญชีจากรายการที่กำหนด', 'danger')
            return render_template('admin/customer_ban.html', customer=user, reason_categories=BAN_REASON_CATEGORIES)

        if reason_category == 'อื่น ๆ โดยต้องกรอกรายละเอียดเพิ่มเติม' and not reason_detail:
            conn.close()
            flash('กรณีเลือกเหตุผลอื่น ๆ จำเป็นต้องกรอกรายละเอียดเพิ่มเติม', 'danger')
            return render_template('admin/customer_ban.html', customer=user, reason_categories=BAN_REASON_CATEGORIES)

        full_reason = f"{reason_category}: {reason_detail}" if reason_detail else reason_category

        cursor = conn.cursor()
        # อัปเดตสถานะบัญชี
        cursor.execute("""
            UPDATE users 
            SET is_banned = 1, banned_at = CURRENT_TIMESTAMP, banned_reason = ? 
            WHERE id = ?
        """, (full_reason, user_id))

        # บันทึกประวัติใน user_ban_logs (ไม่ลบประวัติเดิมเมื่อปลดระงับ)
        cursor.execute("""
            INSERT INTO user_ban_logs (user_id, admin_id, admin_name, action, reason_category, reason_detail)
            VALUES (?, ?, ?, 'ban', ?, ?)
        """, (user_id, session['user_id'], session.get('user_name', 'Admin'), reason_category, reason_detail))

        conn.commit()
        conn.close()

        flash(f'ระงับการใช้งานบัญชีของคุณ {user["name"]} เรียบร้อยแล้ว (เหตุผล: {full_reason})', 'warning')
        return redirect(url_for('admin.customer_detail', user_id=user_id))

    conn.close()
    return render_template('admin/customer_ban.html', customer=user, reason_categories=BAN_REASON_CATEGORIES)


@admin_bp.route('/customer/<int:user_id>/unban', methods=['POST'])
@admin_required
def customer_unban(user_id):
    """ปลดการระงับบัญชีลูกค้า โดยเก็บรักษาประวัติการระงับเดิมไว้ทั้งหมด"""
    unban_notes = request.form.get('notes', '').strip() or 'ปลดการระงับบัญชีโดยผู้ดูแลระบบ'

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        conn.close()
        flash('ไม่พบสมาชิกลูกค้าที่ระบุ', 'danger')
        return redirect(url_for('admin.customers'))

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET is_banned = 0, banned_at = NULL, banned_reason = NULL 
        WHERE id = ?
    """, (user_id,))

    # บันทึกประวัติการปลดระงับใน user_ban_logs
    cursor.execute("""
        INSERT INTO user_ban_logs (user_id, admin_id, admin_name, action, reason_category, reason_detail)
        VALUES (?, ?, ?, 'unban', 'ปลดการระงับบัญชี', ?)
    """, (user_id, session['user_id'], session.get('user_name', 'Admin'), unban_notes))

    conn.commit()
    conn.close()

    flash(f'ปลดการระงับบัญชีของคุณ {user["name"]} เรียบร้อยแล้ว สมาชิกสามารถเข้าสู่ระบบได้ตามปกติ', 'success')
    return redirect(url_for('admin.customer_detail', user_id=user_id))


# ================== จัดการเรื่องแจ้งปัญหา (Support Tickets Management) ==================

@admin_bp.route('/tickets')
@admin_required
def tickets():
    """แสดงรายการเรื่องแจ้งปัญหาทั้งหมดในระบบ พร้อมตัวกรองสถานะ"""
    status_filter = request.args.get('status', '').strip()
    conn = get_db_connection()

    query = """
        SELECT t.*, u.name as customer_name, u.email as customer_email, u.phone as customer_phone,
               o.order_number
        FROM support_tickets t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN orders o ON t.order_id = o.id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND t.status = ?"
        params.append(status_filter)

    query += " ORDER BY CASE WHEN t.status = 'รอตรวจสอบ' THEN 0 WHEN t.status = 'กำลังดำเนินการ' THEN 1 ELSE 2 END, t.id DESC"
    all_tickets = conn.execute(query, params).fetchall()

    pending_count = conn.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'รอตรวจสอบ'").fetchone()[0]
    conn.close()

    return render_template('admin/tickets.html', tickets=all_tickets, current_status=status_filter, pending_count=pending_count)


@admin_bp.route('/ticket/<int:ticket_id>')
@admin_required
def ticket_detail(ticket_id):
    """ดูรายละเอียดเรื่องแจ้งปัญหาและฟอร์มตอบกลับ"""
    conn = get_db_connection()
    ticket = conn.execute("""
        SELECT t.*, u.name as customer_name, u.email as customer_email, u.phone as customer_phone,
               o.order_number, o.status as order_status,
               admin_u.name as admin_responder_name
        FROM support_tickets t
        JOIN users u ON t.user_id = u.id
        LEFT JOIN orders o ON t.order_id = o.id
        LEFT JOIN users admin_u ON t.replied_by = admin_u.id
        WHERE t.id = ?
    """, (ticket_id,)).fetchone()
    conn.close()

    if not ticket:
        flash('ไม่พบเรื่องแจ้งปัญหาที่ระบุ', 'danger')
        return redirect(url_for('admin.tickets'))

    return render_template('admin/ticket_detail.html', ticket=ticket)


@admin_bp.route('/ticket/<int:ticket_id>/reply', methods=['POST'])
@admin_required
def ticket_reply(ticket_id):
    """บันทึกคำตอบและปรับปรุงสถานะเรื่องแจ้งปัญหา"""
    reply_text = request.form.get('admin_reply', '').strip()
    new_status = request.form.get('status', '').strip()

    valid_statuses = ['รอตรวจสอบ', 'กำลังดำเนินการ', 'ตอบกลับแล้ว', 'ปิดเรื่อง']
    if new_status not in valid_statuses:
        flash('สถานะไม่ถูกต้อง', 'danger')
        return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id))

    if not reply_text:
        flash('กรุณากรอกข้อความตอบกลับ', 'danger')
        return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE support_tickets 
        SET admin_reply = ?,
            status = ?,
            replied_by = ?,
            replied_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (reply_text, new_status, session['user_id'], ticket_id))
    conn.commit()
    conn.close()

    flash(f'บันทึกคำตอบและเปลี่ยนสถานะเป็น "{new_status}" เรียบร้อยแล้ว', 'success')
    return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id))


# ================== ประวัติการปรับปรุงสต็อก (Stock Adjustments Audit History) ==================

@admin_bp.route('/stock/history')
@admin_required
def stock_history():
    """แสดงประวัติการปรับปรุงสต็อกทั้งหมด (Audit Log)"""
    conn = get_db_connection()
    history = conn.execute("""
        SELECT sa.*, p.code as product_code, p.model as product_model, p.brand as product_brand
        FROM stock_adjustments sa
        JOIN products p ON sa.product_id = p.id
        ORDER BY sa.id DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return render_template('admin/stock_history.html', history=history)


# ================== สต็อกสินค้า (Stock Management) ==================

@admin_bp.route('/stock')
@admin_required
def stock():
    """ทางลัดเข้าสู่การจัดการสต็อกสินค้า"""
    return redirect(url_for('admin.reports') + '#inventory-section')


# ================== ตั้งค่าเว็บไซต์ (Shop Settings) ==================

@admin_bp.route('/settings')
@admin_required
def settings():
    """หน้าข้อมูลและตั้งค่าร้าน 160 ธีระ สายซิ่ง"""
    from config import SHOP_CONFIG
    return render_template('admin/settings.html', shop_config=SHOP_CONFIG)


