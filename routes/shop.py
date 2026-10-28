"""
routes/shop.py
ระบบแสดงรายการสินค้า หน้าแรก ค้นหา กรองข้อมูล และจัดการตะกร้าสินค้า (Cart)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def home():
    """หน้าแรกของเว็บไซต์ร้านขายรถจักรยานยนต์"""
    conn = get_db_connection()
    
    # 1. รถมอเตอร์ไซค์แนะนำ (Featured 6 รุ่นยอดนิยม)
    featured = conn.execute("""
        SELECT * FROM products 
        WHERE status = 'available' AND stock > 0
        ORDER BY price DESC 
        LIMIT 6
    """).fetchall()

    # 2. จำนวนรถแยกตามประเภท
    categories_stat = conn.execute("""
        SELECT category, COUNT(*) as count 
        FROM products 
        GROUP BY category
    """).fetchall()

    # 3. รถมอเตอร์ไซค์ที่มีสินค้าพร้อมส่ง (In-Stock)
    in_stock_bikes = conn.execute("""
        SELECT * FROM products 
        WHERE status = 'available' AND stock > 0
        ORDER BY id ASC 
        LIMIT 8
    """).fetchall()

    # 4. สรุปภาพรวม
    total_models = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_brands = conn.execute("SELECT COUNT(DISTINCT brand) FROM products").fetchone()[0]

    conn.close()
    return render_template('home.html', 
                           featured=featured, 
                           categories_stat=categories_stat, 
                           in_stock_bikes=in_stock_bikes,
                           total_models=total_models,
                           total_brands=total_brands)


@shop_bp.route('/products')
def products():
    """หน้ารายการรถจักรยานยนต์ทั้งหมด พร้อมระบบค้นหา กรอง และเรียงลำดับ"""
    conn = get_db_connection()

    # ดึงพารามิเตอร์การกรองจาก Query String
    search_q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    cc_range = request.args.get('cc_range', '').strip()
    year = request.args.get('year', '').strip()
    sort_by = request.args.get('sort', 'default').strip()

    # ประกอบ Parameterized SQL Query
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search_q:
        query += " AND (model LIKE ? OR brand LIKE ? OR description LIKE ?)"
        like_term = f"%{search_q}%"
        params.extend([like_term, like_term, like_term])

    if category:
        query += " AND category = ?"
        params.append(category)

    if brand:
        query += " AND brand = ?"
        params.append(brand)

    if year:
        query += " AND model_year = ?"
        params.append(year)

    if cc_range:
        if cc_range == 'under_115':
            query += " AND engine_cc < 115"
        elif cc_range == '115_130':
            query += " AND engine_cc >= 115 AND engine_cc <= 130"
        elif cc_range == '131_160':
            query += " AND engine_cc >= 131 AND engine_cc <= 160"

    # การเรียงลำดับ
    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'cc_desc':
        query += " ORDER BY engine_cc DESC"
    elif sort_by == 'name_asc':
        query += " ORDER BY brand ASC, model ASC"
    else:
        query += " ORDER BY id ASC"

    product_list = conn.execute(query, params).fetchall()

    # ดึงค่าตัวเลือกสำหรับ Dropdown ฟิลเตอร์
    all_categories = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    all_brands = conn.execute("SELECT DISTINCT brand FROM products ORDER BY brand").fetchall()
    all_years = conn.execute("SELECT DISTINCT model_year FROM products ORDER BY model_year DESC").fetchall()

    conn.close()

    return render_template('products.html',
                           products=product_list,
                           search_q=search_q,
                           current_category=category,
                           current_brand=brand,
                           current_cc_range=cc_range,
                           current_year=year,
                           current_sort=sort_by,
                           all_categories=[r['category'] for r in all_categories],
                           all_brands=[r['brand'] for r in all_brands],
                           all_years=[r['model_year'] for r in all_years])


@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """หน้ารายละเอียดรถจักรยานยนต์แต่ละรุ่น พร้อมข้อมูลสเปกทางเทคนิคครบถ้วน"""
    import json
    from specs_data import MOTORCYCLE_SPECS

    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        conn.close()
        flash('ไม่พบข้อมูลรถจักรยานยนต์ที่คุณเลือก', 'danger')
        return redirect(url_for('shop.products'))

    # ดึงสเปกทางเทคนิคจาก specs_json หรือจาก MOTORCYCLE_SPECS
    specs = None
    if 'specs_json' in product.keys() and product['specs_json']:
        try:
            specs = json.loads(product['specs_json'])
        except Exception:
            specs = None
    if not specs and product['code'] in MOTORCYCLE_SPECS:
        specs = MOTORCYCLE_SPECS[product['code']]

    # รถรุ่นอื่นที่ใกล้เคียงกันในประเภทเดียวกัน
    related = conn.execute("""
        SELECT * FROM products 
        WHERE category = ? AND id != ? AND status = 'available'
        LIMIT 4
    """, (product['category'], product_id)).fetchall()

    conn.close()
    return render_template('product_detail.html', product=product, specs=specs, related=related)



# ================== ตะกร้าสินค้า (Cart System) ==================

@shop_bp.route('/cart')
def cart():
    """หน้าตะกร้าสินค้า ดึงข้อมูลราคาและตรวจสอบสต็อกจริงจากฐานข้อมูล"""
    cart_session = session.get('cart', {})
    cart_items = []
    grand_total = 0.0

    if cart_session:
        conn = get_db_connection()
        for p_id_str, qty in list(cart_session.items()):
            try:
                p_id = int(p_id_str)
                product = conn.execute("SELECT * FROM products WHERE id = ?", (p_id,)).fetchone()
                if product:
                    # ตรวจสอบว่าสินค้ายังพร้อมจำหน่ายหรือไม่
                    available_stock = product['stock']
                    actual_qty = min(qty, available_stock) if available_stock > 0 else 0
                    
                    subtotal = product['price'] * actual_qty
                    grand_total += subtotal

                    cart_items.append({
                        'product': product,
                        'requested_qty': qty,
                        'actual_qty': actual_qty,
                        'subtotal': subtotal,
                        'is_out_of_stock': (available_stock == 0 or product['status'] != 'available'),
                        'exceeds_stock': (qty > available_stock)
                    })
                else:
                    # หากสินค้าถูกลบออกจากระบบ ให้เอาออกจากตะกร้า
                    cart_session.pop(p_id_str, None)
                    session.modified = True
            except ValueError:
                continue
        conn.close()

    total_units = sum(item['actual_qty'] for item in cart_items)
    items_count = len(cart_items)

    return render_template('cart.html', 
                           cart_items=cart_items, 
                           grand_total=grand_total,
                           total_units=total_units,
                           items_count=items_count)


def is_ajax():
    """ตรวจสอบว่าเป็นคำขอผ่าน AJAX / Fetch API หรือไม่"""
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.is_json or
        'application/json' in request.headers.get('Accept', '') or
        request.args.get('ajax') == '1'
    )


@shop_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """เพิ่มสินค้าลงตะกร้าพร้อมตรวจสอบสต็อกคงเหลือ รองรับทั้ง AJAX และ Form ธรรมดา"""
    from flask import jsonify

    if request.is_json:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
    else:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', default=1, type=int)

    cart = session.get('cart', {})

    if not product_id or quantity <= 0:
        msg = 'ข้อมูลสินค้าหรือจำนวนไม่ถูกต้อง'
        if is_ajax():
            return jsonify({'success': False, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values())}), 400
        flash(msg, 'danger')
        return redirect(request.referrer or url_for('shop.products'))

    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        msg = 'ไม่พบสินค้านี้ในระบบ'
        if is_ajax():
            return jsonify({'success': False, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values())}), 404
        flash(msg, 'danger')
        return redirect(url_for('shop.products'))

    if product['status'] == 'discontinued':
        msg = 'ขออภัย รถรุ่นนี้เลิกจำหน่ายแล้ว ไม่สามารถสั่งซื้อได้'
        if is_ajax():
            return jsonify({'success': False, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values())}), 400
        flash(msg, 'warning')
        return redirect(url_for('shop.product_detail', product_id=product_id))

    if product['stock'] <= 0 or product['status'] == 'out_of_stock':
        msg = 'ขออภัย สินค้านี้หมดสต็อกชั่วคราว'
        if is_ajax():
            return jsonify({'success': False, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values())}), 400
        flash(msg, 'warning')
        return redirect(url_for('shop.product_detail', product_id=product_id))

    # จัดการเซสชันตะกร้า
    current_in_cart = cart.get(str(product_id), 0)
    new_total_qty = current_in_cart + quantity

    if new_total_qty > product['stock']:
        allowed_add = max(0, product['stock'] - current_in_cart)
        if allowed_add > 0:
            cart[str(product_id)] = product['stock']
            session['cart'] = cart
            session.modified = True
            msg = f'เพิ่มได้เพียง {allowed_add} คัน เนื่องจากสต็อกคงเหลือมี {product["stock"]} คัน'
            if is_ajax():
                return jsonify({'success': True, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values()), 'cart_count': sum(cart.values())})
            flash(msg, 'warning')
        else:
            msg = f'คุณมีสินค้าในตะกร้าครบตามจำนวนสต็อกที่มีอยู่แล้ว ({product["stock"]} คัน)'
            if is_ajax():
                return jsonify({'success': False, 'message': msg, 'cart_items_count': len(cart), 'cart_total_qty': sum(cart.values())}), 400
            flash(msg, 'warning')
        return redirect(url_for('shop.cart'))

    cart[str(product_id)] = new_total_qty
    session['cart'] = cart
    session.modified = True
    msg = f'เพิ่ม {product["model"]} ({quantity} คัน) ลงในตะกร้าเรียบร้อยแล้ว'

    if is_ajax():
        return jsonify({
            'success': True,
            'message': msg,
            'product_model': product['model'],
            'added_qty': quantity,
            'cart_items_count': len(cart),
            'cart_total_qty': sum(cart.values()),
            'cart_count': sum(cart.values())
        })

    flash(msg, 'success')
    return redirect(url_for('shop.cart'))


@shop_bp.route('/cart/update', methods=['POST'])
def update_cart():
    """ปรับจำนวนสินค้าในตะกร้า รองรับทั้ง AJAX และ Form ธรรมดา"""
    from flask import jsonify

    if request.is_json:
        data = request.get_json() or {}
        product_id = data.get('product_id')
        quantity = data.get('quantity')
    else:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', type=int)

    cart = session.get('cart', {})
    p_id_str = str(product_id)
    msg = 'อัปเดตเรียบร้อย'

    if p_id_str in cart:
        if quantity <= 0:
            cart.pop(p_id_str)
            msg = 'ลบสินค้าออกจากตะกร้าเรียบร้อยแล้ว'
            flash(msg, 'info')
        else:
            conn = get_db_connection()
            product = conn.execute("SELECT stock, model, price FROM products WHERE id = ?", (product_id,)).fetchone()
            conn.close()

            if product and quantity > product['stock']:
                cart[p_id_str] = product['stock']
                msg = f'ปรับเป็น {product["stock"]} คัน เนื่องจากสต็อกมีจำกัด'
                flash(msg, 'warning')
            else:
                cart[p_id_str] = quantity
                msg = 'อัปเดตจำนวนสินค้าในตะกร้าเรียบร้อย'
                flash(msg, 'success')

        session['cart'] = cart
        session.modified = True

    if is_ajax():
        return jsonify({
            'success': True,
            'message': msg,
            'cart_items_count': len(cart),
            'cart_total_qty': sum(cart.values()),
            'cart_count': sum(cart.values())
        })

    return redirect(url_for('shop.cart'))


@shop_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """ลบสินค้าชิ้นนั้นออกจากตะกร้า รองรับทั้ง AJAX และ Form ธรรมดา"""
    from flask import jsonify

    cart = session.get('cart', {})
    p_id_str = str(product_id)
    if p_id_str in cart:
        cart.pop(p_id_str)
        session['cart'] = cart
        session.modified = True
        flash('นำสินค้าออกจากตะกร้าแล้ว', 'info')

    if is_ajax():
        return jsonify({
            'success': True,
            'message': 'นำสินค้าออกจากตะกร้าแล้ว',
            'cart_items_count': len(cart),
            'cart_total_qty': sum(cart.values()),
            'cart_count': sum(cart.values())
        })

    return redirect(url_for('shop.cart'))


@shop_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """ล้างตะกร้าสินค้าทั้งหมด"""
    session.pop('cart', None)
    session.modified = True
    flash('ล้างตะกร้าสินค้าเรียบร้อยแล้ว', 'info')
    return redirect(url_for('shop.cart'))
