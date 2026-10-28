"""
app.py
ไฟล์หลักสำหรับเริ่มต้นและรันเว็บแอปพลิเคชัน Flask ร้านขายรถจักรยานยนต์ไม่เกิน 160 cc
"""

import os
import sys

# ปรับการแสดงผลภาษาไทยในคอนโซลของระบบปฏิบัติการ Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from flask import Flask, render_template, session, send_from_directory, url_for
from database import init_db, seed_db, get_db_connection
from config import SHOP_CONFIG

# นำเข้า Blueprints จากโฟลเดอร์ routes
from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.customer import customer_bp
from routes.admin import admin_bp

app = Flask(__name__)

# กำหนด Secret Key สำหรับ Session และ Flash messages
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'moto-shop-secret-key-university-2026-safe')

# กำหนดขนาดไฟล์สูงสุดที่อัปโหลดได้ (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# โฟลเดอร์สำหรับอัปโหลดไฟล์ และโฟลเดอร์รูปภาพต้นฉบับ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'static', 'รูปภาพ')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'ไฟล์ที่ผู้ใช้อัปโหลด')
app.config['UPLOAD_FOLDER_SLIPS'] = os.path.join(UPLOAD_DIR, 'slips')
app.config['UPLOAD_FOLDER_PRODUCTS'] = os.path.join(UPLOAD_DIR, 'products')
app.config['UPLOAD_FOLDER_AVATARS'] = os.path.join(UPLOAD_DIR, 'avatars')

# สร้างโฟลเดอร์สำหรับเก็บไฟล์อัปโหลด
os.makedirs(app.config['UPLOAD_FOLDER_SLIPS'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_PRODUCTS'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_AVATARS'], exist_ok=True)

# Route ให้บริการรูปภาพต้นฉบับจากโฟลเดอร์ รูปภาพ (ไม่แตะต้องหรือเปลี่ยนชื่อไฟล์เดิม)
@app.route('/รูปภาพ/<path:filename>')
@app.route('/shop_images/<path:filename>')
def serve_shop_images(filename):
    file_path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(file_path):
        if ' x ' in filename:
            alt_name = filename.replace(' x ', ' \u00d7 ')
            if os.path.exists(os.path.join(IMAGE_DIR, alt_name)):
                return send_from_directory(IMAGE_DIR, alt_name)
        elif ' \u00d7 ' in filename:
            alt_name = filename.replace(' \u00d7 ', ' x ')
            if os.path.exists(os.path.join(IMAGE_DIR, alt_name)):
                return send_from_directory(IMAGE_DIR, alt_name)
    return send_from_directory(IMAGE_DIR, filename)

# Route ให้บริการไฟล์อัปโหลด (รองรับทั้งภาษาไทยและเส้นทางเดิมเพื่อความเข้ากันได้ 100%)
@app.route('/static/ไฟล์ที่ผู้ใช้อัปโหลด/<path:filename>')
@app.route('/ไฟล์ที่ผู้ใช้อัปโหลด/<path:filename>')
@app.route('/static/uploads/<path:filename>')
@app.route('/uploads/<path:filename>')
def serve_uploaded_files(filename):
    # ตรวจสอบว่าไฟล์อยู่ใน UPLOAD_DIR หรือไม่
    target_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.isfile(target_path):
        return send_from_directory(UPLOAD_DIR, filename)
    # ตรวจสอบใน UPLOAD_FOLDER_PRODUCTS
    prod_path = os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], filename)
    if os.path.isfile(prod_path):
        return send_from_directory(app.config['UPLOAD_FOLDER_PRODUCTS'], filename)
    # ตรวจสอบใน UPLOAD_FOLDER_SLIPS
    slip_path = os.path.join(app.config['UPLOAD_FOLDER_SLIPS'], filename)
    if os.path.isfile(slip_path):
        return send_from_directory(app.config['UPLOAD_FOLDER_SLIPS'], filename)
    # ตรวจสอบใน UPLOAD_FOLDER_AVATARS
    avatar_path = os.path.join(app.config['UPLOAD_FOLDER_AVATARS'], filename)
    if os.path.isfile(avatar_path):
        return send_from_directory(app.config['UPLOAD_FOLDER_AVATARS'], filename)
    return send_from_directory(UPLOAD_DIR, filename)

# ลงทะเบียน Blueprints
app.register_blueprint(shop_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(admin_bp)


# Jinja Custom Filters สำหรับจัดรูปแบบตัวเลขและเงิน
@app.template_filter('currency')
def currency_filter(value):
    """แปลงตัวเลขเป็นรูปแบบเงินบาทมีคอมม่า เช่น 44,400.00"""
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return value


@app.template_filter('thai_date')
def thai_date_filter(date_str):
    """จัดรูปแบบวันเวลาให้อ่านง่าย"""
    if not date_str:
        return '-'
    try:
        # ตัดเหลือเฉพาะ วันที่ และ เวลา
        return str(date_str)[:19]
    except Exception:
        return str(date_str)


@app.template_filter('bike_img')
def bike_img_filter(image_url):
    """
    จัดหา URL ของรูปภาพรถมอเตอร์ไซค์
    - รองรับรูปภาพที่อัปโหลดใหม่ใน static/ไฟล์ที่ผู้ใช้อัปโหลด/products/
    - รองรับรูปภาพต้นฉบับในโฟลเดอร์ รูปภาพ/รถมอเตอร์ไซค์
    - รองรับ fallback ไปยัง placeholder_bike.svg อย่างปลอดภัย
    """
    if not image_url:
        return url_for('static', filename='images/placeholder_bike.svg')
    
    clean_url = str(image_url).strip()
    
    # 1. กรณีขึ้นต้นด้วยโฟลเดอร์ รูปภาพ
    if clean_url.startswith('รถมอเตอร์ไซค์/') or clean_url.startswith('โลโก้/') or clean_url.startswith('แบนเนอร์/'):
        return f"/รูปภาพ/{clean_url}"
    if clean_url.startswith('/รูปภาพ/'):
        return clean_url
        
    # 2. กรณีขึ้นต้นด้วย uploads หรือ ไฟล์ที่ผู้ใช้อัปโหลด
    if clean_url.startswith('ไฟล์ที่ผู้ใช้อัปโหลด/'):
        subpath = clean_url.replace('ไฟล์ที่ผู้ใช้อัปโหลด/', '')
        return f"/uploads/{subpath}"
    if clean_url.startswith('/static/ไฟล์ที่ผู้ใช้อัปโหลด/'):
        subpath = clean_url.replace('/static/ไฟล์ที่ผู้ใช้อัปโหลด/', '')
        return f"/uploads/{subpath}"
    if clean_url.startswith('uploads/'):
        return f"/{clean_url}"
    if clean_url.startswith('/uploads/'):
        return clean_url

    # 3. ตรวจสอบว่าไฟล์อยู่ใน static/ไฟล์ที่ผู้ใช้อัปโหลด/products หรือไม่ (เช่น prod_xxx.jpeg)
    prod_file = os.path.join(app.config['UPLOAD_FOLDER_PRODUCTS'], clean_url)
    if os.path.exists(prod_file):
        return f"/uploads/products/{clean_url}"

    # 4. ตรวจสอบว่าอยู่ใน static/ไฟล์ที่ผู้ใช้อัปโหลด โดยตรงหรือไม่
    up_file = os.path.join(UPLOAD_DIR, clean_url)
    if os.path.exists(up_file):
        return f"/uploads/{clean_url}"

    # 5. ตรวจสอบไฟล์ใน static/images/
    static_file = os.path.join(BASE_DIR, 'static', 'images', clean_url)
    if os.path.exists(static_file):
        return url_for('static', filename='images/' + clean_url)
    
    # 6. ตรวจสอบไฟล์ใน รูปภาพ/รถมอเตอร์ไซค์/
    bike_file = os.path.join(IMAGE_DIR, 'รถมอเตอร์ไซค์', clean_url)
    if os.path.exists(bike_file):
        return f"/รูปภาพ/รถมอเตอร์ไซค์/{clean_url}"
    
    # 7. ตรวจสอบใน รูปภาพ/ โดยตรง
    direct_file = os.path.join(IMAGE_DIR, clean_url)
    if os.path.exists(direct_file):
        return f"/รูปภาพ/{clean_url}"

    # 8. หากชื่อไฟล์ขึ้นต้นด้วย prod_ ให้ส่งผ่าน /uploads/products/
    if clean_url.startswith('prod_'):
        return f"/uploads/products/{clean_url}"
        
    return url_for('static', filename='images/placeholder_bike.svg')


# เพิ่มตัวแปรส่วนกลางใน Jinja Environment (สามารถเรียกใช้ได้ทั้งในเทมเพลตและ Macros ที่ import)
app.jinja_env.globals['shop_config'] = SHOP_CONFIG
app.jinja_env.globals['bike_img'] = bike_img_filter

# Context Processors เพื่อให้ทุก Template สามารถเข้าถึงตัวแปรเหล่านี้ได้อัตโนมัติ
@app.context_processor
def inject_global_data():
    cart = session.get('cart', {})
    cart_items_count = len(cart) if cart else 0
    cart_total_qty = sum(cart.values()) if cart else 0
    cart_count = cart_total_qty  # คงชื่อเดิมเพื่อ backward compatibility

    current_user = None
    if 'user_id' in session:
        conn = get_db_connection()
        current_user = conn.execute(
            "SELECT id, name, email, role, phone, address, avatar, is_banned, banned_reason FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
        conn.close()

        # หากผู้ใช้ถูกระงับการใช้งาน ให้ตัดเซสชันทันทีเพื่อความปลอดภัย
        if current_user and current_user['is_banned']:
            session.clear()
            current_user = None

    return {
        'cart_count': cart_count,
        'cart_items_count': cart_items_count,
        'cart_total_qty': cart_total_qty,
        'current_user': current_user,
        'is_logged_in': 'user_id' in session and current_user is not None,
        'is_admin': session.get('user_role') == 'admin',
        'shop_config': SHOP_CONFIG,
        'bike_img': bike_img_filter
    }


# จัดการ Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', not_found=True), 404


@app.errorhandler(403)
def access_forbidden(e):
    return render_template('base.html', forbidden=True), 403


# เริ่มต้นระบบฐานข้อมูลและ Seed ข้อมูลตัวอย่างเมื่อเปิดแอปพลิเคชัน
with app.app_context():
    init_db()
    seed_db()


if __name__ == '__main__':
    print("==================================================")
    print("   160 ธีระ สายซิ่ง (160 TEERA SAI SING) FLASK   ")
    print("   ศูนย์รวมรถจักรยานยนต์ความจุไม่เกิน 160 cc     ")
    print("==================================================")
    print(" • เปิดเว็บไซต์ที่: http://127.0.0.1:5000")
    print(" • บัญชีผู้ดูแลระบบ (Admin): admin@bikeshop.com | รหัส: admin1234")
    print(" • บัญชีลูกค้าทดสอบ (Customer): customer@test.com | รหัส: customer1234")
    print(" • เวลาทำการ: วันพุธ 09:00 - 18:00 น.")
    print("==================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
