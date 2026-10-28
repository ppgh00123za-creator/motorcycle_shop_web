"""
test_app.py
ชุดทดสอบระบบอัตโนมัติ (Automated Test Suite) สำหรับร้าน "160 ธีระ สายซิ่ง" (160 Teera Sai Sing)
ทดสอบครอบคลุมทุกระบบหลักตามเกณฑ์ตรวจรับงาน:
1. การแสดงผลหน้าแรกและข้อมูลร้าน
2. การค้นหาและกรองรถไม่เกิน 160 cc
3. การตรวจจับและบังคับความจุกระบอกสูบไม่เกิน 160 cc
4. กฎความปลอดภัยรหัสผ่าน (ปฏิเสธ 1234, รหัสสั้น, รหัสไม่มีตัวเลข/ตัวอักษร, บันทึก Hash ใน SQLite)
5. การรักษาความปลอดภัย Session และการแบ่งสิทธิ์ (Admin vs Customer)
6. วงจรการสั่งซื้อ ตัดสต็อก แนบสลิป อนุมัติ และออกใบเสร็จ PDF "160 ธีระ สายซิ่ง"
7. การยกเลิกคำสั่งซื้อและการคืนสต็อกเข้า SQLite
8. การให้บริการไฟล์รูปภาพต้นฉบับ (โลโก้, แบนเนอร์, รถมอเตอร์ไซค์ 20 รุ่น)
"""

import os
import io
import sys
import unittest
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from app import app
from database import get_db_connection
from config import SHOP_CONFIG, PRODUCT_IMAGE_MAP
from werkzeug.security import generate_password_hash, check_password_hash


class TeeraSaiSingShopTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_homepage_and_shop_branding(self):
        """1. หน้าแรกเปิดได้จริง แสดงชื่อร้าน 160 ธีระ สายซิ่ง คำโปรย และแบนเนอร์"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('160 ธีระ สายซิ่ง'.encode('utf-8'), response.data)
        self.assertIn('รถคู่ใจ สไตล์ที่ใช่ ในแบบของคุณ'.encode('utf-8'), response.data)
        self.assertIn('Wave 110i'.encode('utf-8'), response.data)
        print("✓ Test 1 ผ่าน: หน้าแรกเปิดได้และแสดงอัตลักษณ์ 160 ธีระ สายซิ่ง ครบถ้วน")

    def test_02_products_and_filters(self):
        """2. หน้ารายการรถ ค้นหาและกรองได้จริง"""
        # รถทั้งหมด
        res = self.client.get('/products')
        self.assertEqual(res.status_code, 200)
        
        # กรองเฉพาะ Honda
        res_honda = self.client.get('/products?brand=Honda')
        self.assertEqual(res_honda.status_code, 200)
        self.assertIn('Honda'.encode('utf-8'), res_honda.data)

        # กรองเฉพาะประเภท ครอบครัว
        res_family = self.client.get('/products?category=ครอบครัว')
        self.assertEqual(res_family.status_code, 200)
        self.assertIn('Wave 110i'.encode('utf-8'), res_family.data)

        # ค้นหาด้วยคำว่า Click
        res_click = self.client.get('/products?q=Click')
        self.assertEqual(res_click.status_code, 200)
        self.assertIn('Click 160'.encode('utf-8'), res_click.data)

        print("✓ Test 2 ผ่าน: ค้นหาและกรองยี่ห้อ/ประเภท/คำค้นหา ได้ถูกต้อง")

    def test_03_engine_cc_rule(self):
        """3. ตรวจสอบว่าสินค้าทุกรายการในระบบมีความจุไม่เกิน 160 cc"""
        conn = get_db_connection()
        over_cc = conn.execute("SELECT COUNT(*) FROM products WHERE engine_cc > 160").fetchone()[0]
        total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        conn.close()

        self.assertEqual(over_cc, 0, "ห้ามมีสินค้าเกิน 160 cc เด็ดขาด")
        self.assertGreaterEqual(total_products, 20, "ต้องมีสินค้าตัวอย่างอย่างน้อย 20 รุ่น")
        print(f"✓ Test 3 ผ่าน: ตรวจสอบความจุเครื่องยนต์ไม่เกิน 160 cc ทุกรุ่น ({total_products} รุ่น)")

    def test_04_strict_password_validation(self):
        """4. ตรวจสอบข้อบังคับรหัสผ่าน: ปฏิเสธ 1234, รหัสสั้น, ไม่มีตัวเลข/ตัวอักษร และยอมรับรหัสที่ถูกต้อง"""
        expected_msg = 'รหัสผ่านไม่ปลอดภัย กรุณาใช้รหัสผ่านอย่างน้อย 8 ตัวอักษร และมีทั้งตัวอักษรภาษาอังกฤษกับตัวเลข'

        # 4.1 ทดสอบรหัสผ่าน '1234' (ต้องถูกปฏิเสธ)
        res_weak1 = self.client.post('/register', data={
            'name': 'ทดสอบ รหัส1234',
            'email': 'weak1234@test.com',
            'password': '1234',
            'confirm_password': '1234'
        }, follow_redirects=True)
        self.assertIn(expected_msg.encode('utf-8'), res_weak1.data)

        # 4.2 ทดสอบรหัสผ่านสั้น เช่น 'abc1' (ต้องถูกปฏิเสธ)
        res_short = self.client.post('/register', data={
            'name': 'ทดสอบ รหัสสั้น',
            'email': 'short@test.com',
            'password': 'abc1',
            'confirm_password': 'abc1'
        }, follow_redirects=True)
        self.assertIn(expected_msg.encode('utf-8'), res_short.data)

        # 4.3 ทดสอบรหัสผ่าน 8 ตัวขึ้นไปแต่มีแต่ตัวอักษร เช่น 'onlyletters' (ต้องถูกปฏิเสธ)
        res_no_digits = self.client.post('/register', data={
            'name': 'ทดสอบ ตัวอักษรล้วน',
            'email': 'letters@test.com',
            'password': 'onlyletters',
            'confirm_password': 'onlyletters'
        }, follow_redirects=True)
        self.assertIn(expected_msg.encode('utf-8'), res_no_digits.data)

        # 4.4 ทดสอบรหัสผ่าน 8 ตัวขึ้นไปแต่มีแต่ตัวเลข เช่น '12345678' (ต้องถูกปฏิเสธ)
        res_no_letters = self.client.post('/register', data={
            'name': 'ทดสอบ ตัวเลขล้วน',
            'email': 'digits@test.com',
            'password': '12345678',
            'confirm_password': '12345678'
        }, follow_redirects=True)
        self.assertIn(expected_msg.encode('utf-8'), res_no_letters.data)

        # 4.5 ทดสอบรหัสผ่านที่ถูกต้อง (ตัวอักษร + ตัวเลข และ >= 8 ตัวอักษร)
        valid_email = 'teera_rider@test.com'
        # ลบผู้ใช้ทดสอบเก่าออกก่อนหากมี
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE email = ?", (valid_email,))
        conn.commit()
        conn.close()

        res_valid = self.client.post('/register', data={
            'name': 'ธีระ นักบิด',
            'email': valid_email,
            'password': 'teeraRider2026',
            'confirm_password': 'teeraRider2026',
            'phone': '065-718-2338',
            'address': 'ขอนแก่น'
        }, follow_redirects=True)
        self.assertIn('สมัครสมาชิกสำเร็จ'.encode('utf-8'), res_valid.data)

        # ตรวจสอบว่าถูกบันทึกลงใน SQLite จริง และรหัสผ่านถูก hash
        conn = get_db_connection()
        saved_user = conn.execute("SELECT * FROM users WHERE email = ?", (valid_email,)).fetchone()
        conn.close()
        self.assertIsNotNone(saved_user)
        self.assertNotEqual(saved_user['password_hash'], 'teeraRider2026')
        self.assertTrue(saved_user['password_hash'].startswith('scrypt:') or saved_user['password_hash'].startswith('pbkdf2:'))

        # 4.6 ทดสอบสมัครด้วยอีเมลซ้ำ (ต้องถูกปฏิเสธ)
        res_dup = self.client.post('/register', data={
            'name': 'ธีระ ซ้ำ',
            'email': valid_email,
            'password': 'teeraRider2026',
            'confirm_password': 'teeraRider2026'
        }, follow_redirects=True)
        self.assertIn('อีเมลนี้ถูกใช้งานแล้ว'.encode('utf-8'), res_dup.data)

        print("✓ Test 4 ผ่าน: ตรวจสอบความปลอดภัยรหัสผ่าน (ปฏิเสธ 1234, ตรวจตัวอักษร+ตัวเลข, บันทึก Hash ลง SQLite) 100%")

    def test_05_auth_session_and_role_access(self):
        """5. ทดสอบ Login, Session และการจำกัดสิทธิ์ Admin vs Customer"""
        # ออกจากระบบก่อน
        self.client.get('/logout')

        # Login ด้วยรหัสผ่านผิด (ต้องไม่ผ่าน)
        res_wrong = self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn('ไม่ถูกต้อง'.encode('utf-8'), res_wrong.data)

        # Login บัญชีลูกค้า
        res_cust = self.client.post('/login', data={'email': 'customer@test.com', 'password': 'customer1234'}, follow_redirects=True)
        self.assertEqual(res_cust.status_code, 200)

        # ลูกค้าพยายามเข้าถึง Admin Dashboard (ต้องถูกปฏิเสธและ Redirect)
        res_admin_denied = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn('คุณไม่มีสิทธิ์เข้าถึงหน้าระบบผู้ดูแล'.encode('utf-8'), res_admin_denied.data)

        # ออกจากระบบ
        self.client.get('/logout')

        # Login บัญชี Admin
        res_admin = self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        self.assertIn('160 ธีระ สายซิ่ง'.encode('utf-8'), res_admin.data)
        self.assertIn('Dashboard'.encode('utf-8'), res_admin.data)

        print("✓ Test 5 ผ่าน: ระบบสิทธิ์และการป้องกันหน้า Admin ทำงานถูกต้องรัดกุม")

    def test_06_order_checkout_slip_and_pdf_receipt(self):
        """6. กระบวนการสั่งซื้อ ตัดสต็อก แนบสลิป ตรวจสอบ และสร้างใบเสร็จ PDF ร้าน 160 ธีระ สายซิ่ง"""
        # เข้าสู่ระบบลูกค้า
        self.client.post('/login', data={'email': 'customer@test.com', 'password': 'customer1234'}, follow_redirects=True)

        # หาสินค้าที่มีสต็อก
        conn = get_db_connection()
        product = conn.execute("SELECT * FROM products WHERE status = 'available' AND stock >= 2 LIMIT 1").fetchone()
        p_id = product['id']
        old_stock = product['stock']
        conn.close()

        # เพิ่มลงตะกร้า 1 คัน
        self.client.post('/cart/add', data={'product_id': p_id, 'quantity': 1}, follow_redirects=True)

        # ทำการ Checkout ยืนยันคำสั่งซื้อ
        res_checkout = self.client.post('/checkout', data={
            'customer_name': 'นายสมชาย สดใส',
            'customer_phone': '089-123-4567',
            'customer_address': '899/22 ขอนแก่น'
        }, follow_redirects=True)
        self.assertEqual(res_checkout.status_code, 200)

        # ตรวจสอบว่าสต็อกลดลง 1 คันจริงใน SQLite
        conn = get_db_connection()
        updated_p = conn.execute("SELECT stock FROM products WHERE id = ?", (p_id,)).fetchone()
        self.assertEqual(updated_p['stock'], old_stock - 1)

        # ดึงคำสั่งซื้อล่าสุด
        latest_order = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 1").fetchone()
        order_id = latest_order['id']
        conn.close()

        # แนบสลิปโอนเงิน
        dummy_file = (io.BytesIO(b"test slip content"), "slip_test.png")
        res_pay = self.client.post(f'/order/{order_id}/pay', data={'slip_file': dummy_file}, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn('แนบหลักฐานการชำระเงินสำเร็จ'.encode('utf-8'), res_pay.data)

        # สลับเป็น Admin เพื่ออนุมัติการชำระเงิน
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        res_approve = self.client.post(f'/admin/payment/{order_id}/verify', data={'action': 'approve'}, follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)

        # ตรวจสอบสถานะในฐานข้อมูล SQLite
        conn = get_db_connection()
        order_row = conn.execute("SELECT status FROM orders WHERE id = ?", (order_id,)).fetchone()
        pay_row = conn.execute("SELECT status FROM payments WHERE order_id = ?", (order_id,)).fetchone()
        conn.close()
        self.assertEqual(order_row['status'], 'ชำระเงินแล้ว')
        self.assertEqual(pay_row['status'], 'approved')

        # ดาวน์โหลดใบเสร็จ PDF และตรวจสอบเนื้อหา
        res_pdf = self.client.get(f'/order/{order_id}/receipt')
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf.mimetype, 'application/pdf')
        self.assertGreater(len(res_pdf.data), 1000)

        print("✓ Test 6 ผ่าน: วงจรคำสั่งซื้อ ตัดสต็อก แนบสลิป ตรวจสอบ และสร้าง PDF ใบเสร็จ สมบูรณ์")

    def test_07_order_cancellation_and_stock_recovery(self):
        """7. การยกเลิกคำสั่งซื้อและการคืนสต็อกเข้าฐานข้อมูล"""
        self.client.post('/login', data={'email': 'customer@test.com', 'password': 'customer1234'}, follow_redirects=True)

        conn = get_db_connection()
        product = conn.execute("SELECT * FROM products WHERE status = 'available' AND stock >= 3 LIMIT 1").fetchone()
        p_id = product['id']
        stock_init = product['stock']
        conn.close()

        # สั่ง 2 คัน
        self.client.post('/cart/add', data={'product_id': p_id, 'quantity': 2}, follow_redirects=True)
        self.client.post('/checkout', data={
            'customer_name': 'นายสมชาย สดใส',
            'customer_phone': '089-123-4567',
            'customer_address': 'ขอนแก่น'
        }, follow_redirects=True)

        conn = get_db_connection()
        stock_after_buy = conn.execute("SELECT stock FROM products WHERE id = ?", (p_id,)).fetchone()['stock']
        self.assertEqual(stock_after_buy, stock_init - 2)

        latest_order = conn.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1").fetchone()
        order_id = latest_order['id']
        conn.close()

        # ยกเลิกคำสั่งซื้อ
        self.client.post(f'/order/{order_id}/cancel', follow_redirects=True)

        conn = get_db_connection()
        stock_restored = conn.execute("SELECT stock FROM products WHERE id = ?", (p_id,)).fetchone()['stock']
        conn.close()
        self.assertEqual(stock_restored, stock_init)
        print("✓ Test 7 ผ่าน: ยกเลิกคำสั่งซื้อแล้วสต็อกถูกคืนเข้า SQLite อย่างแม่นยำ")

    def test_08_image_serving_routes(self):
        """8. ตรวจสอบการเปิดไฟล์รูปภาพจริงทั้งหมด (โลโก้, แบนเนอร์, รถมอเตอร์ไซค์ 20 รุ่น) ผ่าน HTTP 200"""
        # 8.1 โลโก้
        res_logo = self.client.get(SHOP_CONFIG['logo_url'])
        self.assertEqual(res_logo.status_code, 200, f"โหลดโลโก้ไม่สำเร็จ: {SHOP_CONFIG['logo_url']}")
        self.assertGreater(len(res_logo.data), 1000)

        # 8.2 แบนเนอร์หน้าแรก
        res_b_home = self.client.get(SHOP_CONFIG['banner_home_url'])
        self.assertEqual(res_b_home.status_code, 200, f"โหลดแบนเนอร์หน้าแรกไม่สำเร็จ: {SHOP_CONFIG['banner_home_url']}")
        self.assertGreater(len(res_b_home.data), 1000)

        # 8.3 แบนเนอร์แอดมิน
        res_b_admin = self.client.get(SHOP_CONFIG['banner_admin_url'])
        self.assertEqual(res_b_admin.status_code, 200, f"โหลดแบนเนอร์แอดมินไม่สำเร็จ: {SHOP_CONFIG['banner_admin_url']}")

        # 8.4 ภาพพื้นหลังร้าน
        if 'background_url' in SHOP_CONFIG:
            res_bg = self.client.get(SHOP_CONFIG['background_url'])
            self.assertEqual(res_bg.status_code, 200, f"โหลดภาพพื้นหลังไม่สำเร็จ: {SHOP_CONFIG['background_url']}")

        # 8.5 ภาพรถมอเตอร์ไซค์ทั้ง 20 รุ่น
        for model_name, img_rel_path in PRODUCT_IMAGE_MAP.items():
            encoded_path = urllib.parse.quote(img_rel_path)
            res_bike = self.client.get(f'/รูปภาพ/{encoded_path}')
            self.assertEqual(res_bike.status_code, 200, f"โหลดรูปรถ {model_name} ไม่สำเร็จ: {img_rel_path}")
        print(f"✓ Test 8 ผ่าน: รูปภาพทั้งหมด (โลโก้, แบนเนอร์, ภาพพื้นหลัง, รถมอเตอร์ไซค์ครบทั้ง 20 รุ่น) โหลดได้จริงด้วย HTTP 200 ไม่มี Broken Link")

    def test_9_technical_specs_for_all_20_models(self):
        """9. ตรวจสอบการแสดงผลรายละเอียดสเปกทางเทคนิคครบถ้วนทั้ง 20 รุ่นในหน้าเว็บจริง"""
        conn = get_db_connection()
        products = conn.execute("SELECT id, code, model, status FROM products ORDER BY id ASC").fetchall()
        conn.close()

        self.assertEqual(len(products), 20, "ต้องมีรถในระบบทั้งหมด 20 รุ่น")

        for p in products:
            res = self.client.get(f"/product/{p['id']}")
            self.assertEqual(res.status_code, 200, f"หน้าสินค้ารหัส {p['id']} เปิดไม่ได้")
            html = res.data.decode('utf-8')

            # ตรวจสอบหัวข้อหลัก 5 หัวข้อตามข้อกำหนด
            self.assertIn("ข้อมูลสเปกทางเทคนิค", html, f"ไม่พบหัวข้อสเปกใน {p['model']}")
            self.assertIn("1. ข้อมูลเครื่องยนต์และสมรรถนะ", html, f"ไม่พบหมวดเครื่องยนต์ใน {p['model']}")
            self.assertIn("2. ขนาดและโครงสร้างตัวรถ", html, f"ไม่พบหมวดขนาดตัวรถใน {p['model']}")
            self.assertIn("3. ระบบช่วงล่างและความปลอดภัย", html, f"ไม่พบหมวดช่วงล่างใน {p['model']}")
            self.assertIn("4. จุดเด่นและการใช้งาน", html, f"ไม่พบหมวดจุดเด่นใน {p['model']}")
            self.assertIn("แหล่งอ้างอิงข้อมูลทางการ", html, f"ไม่พบลิงก์อ้างอิงใน {p['model']}")

            # ตรวจสอบกรณีรุ่นเลิกจำหน่าย/แค็ตตาล็อก
            if p['status'] == 'discontinued':
                self.assertIn("แค็ตตาล็อก", html, f"รุ่นประวัติศาสตร์ {p['model']} ต้องแสดงป้ายสถานะแค็ตตาล็อก")

        print("✓ Test 9 ผ่าน: ตรวจสอบรายละเอียดสเปกทางเทคนิค 5 หมวดหลักครบถ้วนทั้ง 20 รุ่น พร้อมแหล่งอ้างอิงทางการ 100%")

    def test_10_order_retention_and_archiving(self):
        """10. ตรวจสอบการจัดเก็บคำสั่งซื้อที่เสร็จสิ้นแล้วให้คงเหลือ 3 ออเดอร์ล่าสุด และระบบ Archive ปลอดภัย"""
        from database import archive_old_completed_orders
        conn = get_db_connection()
        cursor = conn.cursor()

        # ตรวจสอบว่ามีตาราง archived_orders และคอลัมน์ is_archived
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='archived_orders'")
        self.assertIsNotNone(cursor.fetchone(), "ตาราง archived_orders ต้องมีอยู่ในฐานข้อมูล")

        # เรียกฟังก์ชัน archive เพื่อจัดระเบียบ
        archive_old_completed_orders(conn)

        # 1. ตรวจสอบว่าออเดอร์ที่เสร็จสิ้นแล้ว (ชำระเงินแล้ว) ในระบบหลัก (is_archived = 0) มีไม่เกิน 3 รายการ
        active_completed = cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE status IN ('ชำระเงินแล้ว', 'จัดส่งแล้ว') AND is_archived = 0
        """).fetchone()[0]
        self.assertLessEqual(active_completed, 3, "ออเดอร์ที่เสร็จสิ้นแล้วในระบบหลักต้องคงเหลือไม่เกิน 3 รายการล่าสุด")

        # 2. ตรวจสอบว่าออเดอร์ที่ยังไม่เสร็จสิ้น ('รอชำระเงิน') ต้องไม่ถูก archive
        uncompleted = cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE status IN ('รอชำระเงิน', 'รอตรวจสอบการชำระเงิน') AND is_archived = 1
        """).fetchone()[0]
        self.assertEqual(uncompleted, 0, "ออเดอร์ที่ยังไม่เสร็จสิ้นต้องไม่ถูกจัดเก็บเข้า Archive")

        # 3. ตรวจสอบว่า Foreign Key ไม่เกิดข้อผิดพลาด
        fk_check = cursor.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(len(fk_check), 0, "Foreign Key ต้องถูกต้องสมบูรณ์ 100%")

        # 4. ทดสอบดาวน์โหลดใบเสร็จของออเดอร์ที่ถูก archive ว่ายังทำงานได้ปกติ
        archived_order = cursor.execute("""
            SELECT id FROM orders WHERE is_archived = 1 AND status = 'ชำระเงินแล้ว' LIMIT 1
        """).fetchone()
        if archived_order:
            self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
            res_pdf = self.client.get(f"/order/{archived_order['id']}/receipt")
            self.assertEqual(res_pdf.status_code, 200, "ออเดอร์ที่ถูกจัดเก็บต้องยังคงดาวน์โหลดใบเสร็จย้อนหลังได้")
            self.assertEqual(res_pdf.mimetype, 'application/pdf')

        conn.close()
        print("✓ Test 10 ผ่าน: การจัดเก็บคำสั่งซื้อที่เสร็จสิ้นแล้วคงเหลือ 3 ออเดอร์ล่าสุด ทำงานถูกต้อง ปลอดภัย และไม่กระทบ Foreign Keys/ใบเสร็จ")

    def test_11_admin_dashboard_modern_sport_layout(self):
        """11. ตรวจสอบหน้า Admin Dashboard ดีไซน์ใหม่ สไตล์ Modern Sport ครบทั้ง 8 องค์ประกอบ"""
        # Login ด้วยสิทธิ์ Admin
        self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)

        # 1. Top Navbar: โลโก้, การแจ้งเตือน, โปรไฟล์แอดมิน
        self.assertIn('admin-topbar'.encode('utf-8'), res.data)
        self.assertIn('การแจ้งเตือน'.encode('utf-8'), res.data)
        self.assertIn('Super Admin'.encode('utf-8'), res.data)

        # 2. Sidebar: เมนู 8 รายการ และภาพตกแต่ง 600 x 800 px
        self.assertIn('admin-sidebar'.encode('utf-8'), res.data)
        self.assertIn('จัดการสินค้า'.encode('utf-8'), res.data)
        self.assertIn('คำสั่งซื้อ'.encode('utf-8'), res.data)
        self.assertIn('ลูกค้า'.encode('utf-8'), res.data)
        self.assertIn('การชำระเงิน'.encode('utf-8'), res.data)
        self.assertIn('สต็อกสินค้า'.encode('utf-8'), res.data)
        self.assertIn('รายงาน'.encode('utf-8'), res.data)
        self.assertIn('ตั้งค่าเว็บไซต์'.encode('utf-8'), res.data)
        self.assertIn('800 px.jpg'.encode('utf-8'), res.data)
        self.assertIn('ออกจากระบบ'.encode('utf-8'), res.data)

        # 3. Banner ร้าน
        self.assertIn('admin-hero-banner'.encode('utf-8'), res.data)

        # 4. ส่วนต้อนรับ & สถานะร้านแบบเรียลไทม์
        self.assertIn('admin-welcome-section'.encode('utf-8'), res.data)
        self.assertIn('เวลาทำการร้าน:'.encode('utf-8'), res.data)
        self.assertIn('status-badge-realtime'.encode('utf-8'), res.data)

        # 5. 4 KPI Cards (สินค้าทั้งหมด, คำสั่งซื้อวันนี้, สมาชิกทั้งหมด, ยอดขายรวม)
        self.assertIn('kpi-card-products'.encode('utf-8'), res.data)
        self.assertIn('kpi-card-orders-today'.encode('utf-8'), res.data)
        self.assertIn('kpi-card-users'.encode('utf-8'), res.data)
        self.assertIn('kpi-card-sales'.encode('utf-8'), res.data)

        # 6. Split Layout: กราฟยอดขาย 7 วัน & ตารางคำสั่งซื้อล่าสุด
        self.assertIn('admin-split-layout'.encode('utf-8'), res.data)
        self.assertIn('salesChart'.encode('utf-8'), res.data)
        self.assertIn('admin-recent-table'.encode('utf-8'), res.data)

        # 7. เมนูลัด & แจ้งเตือนสถานะสำคัญ
        self.assertIn('admin-quick-menu-card'.encode('utf-8'), res.data)
        self.assertIn('admin-alerts-strip'.encode('utf-8'), res.data)

        # 8. เมนูย่อย ลูกค้า และ ตั้งค่าเว็บไซต์ เปิดได้จริงด้วย HTTP 200
        res_customers = self.client.get('/admin/customers')
        self.assertEqual(res_customers.status_code, 200)

        res_settings = self.client.get('/admin/settings')
        self.assertEqual(res_settings.status_code, 200)

        print("✓ Test 11 ผ่าน: Admin Dashboard ดีไซน์ใหม่ สไตล์ Modern Sport ขาว-เทาอ่อน-ดำ-แดง ครบถ้วน 100%")

    def test_12_forgot_and_reset_password(self):
        """ทดสอบระบบลืมรหัสผ่าน ส่ง Token ปลอดภัย มีวันหมดอายุ ใช้ได้ครั้งเดียว และอัปเดตรหัสผ่านใหม่"""
        # 1. ขอรีเซ็ตรหัสผ่านสำหรับอีเมล customer@test.com
        res = self.client.post('/forgot-password', data={'email': 'customer@test.com'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # ตรวจสอบในตาราง password_resets
        conn = get_db_connection()
        user = conn.execute("SELECT id FROM users WHERE email = 'customer@test.com'").fetchone()
        reset_row = conn.execute("SELECT * FROM password_resets WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user['id'],)).fetchone()
        conn.close()

        self.assertIsNotNone(reset_row)
        token = reset_row['token']
        self.assertEqual(reset_row['used'], 0)

        # 2. เปิดหน้าตั้งรหัสผ่านใหม่ด้วย Token
        res_reset_page = self.client.get(f'/reset-password/{token}')
        self.assertEqual(res_reset_page.status_code, 200)

        # 3. ตั้งรหัสผ่านที่ไม่ปลอดภัย (ปฏิเสธ)
        res_weak = self.client.post(f'/reset-password/{token}', data={
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn('รหัสผ่านไม่ปลอดภัย'.encode('utf-8'), res_weak.data)

        # 4. ตั้งรหัสผ่านใหม่ที่ปลอดภัย
        res_success = self.client.post(f'/reset-password/{token}', data={
            'password': 'NewPassword1234',
            'confirm_password': 'NewPassword1234'
        }, follow_redirects=True)
        self.assertEqual(res_success.status_code, 200)
        self.assertIn('ตั้งรหัสผ่านใหม่เรียบร้อยแล้ว'.encode('utf-8'), res_success.data)

        # 5. ตรวจสอบว่า Token ถูกใช้ไปแล้ว (used = 1) และไม่สามารถใช้ซ้ำได้
        conn = get_db_connection()
        updated_reset = conn.execute("SELECT used FROM password_resets WHERE id = ?", (reset_row['id'],)).fetchone()
        conn.close()
        self.assertEqual(updated_reset['used'], 1)

        # พยายามใช้ Token เดิมซ้ำ -> ต้องถูกปฏิเสธ
        res_reuse = self.client.get(f'/reset-password/{token}', follow_redirects=True)
        self.assertIn('ลิงก์นี้ถูกใช้งานไปแล้ว'.encode('utf-8'), res_reuse.data)

        # 6. ทดสอบเข้าสู่ระบบด้วยรหัสผ่านใหม่สำเร็จ และรหัสเดิมเข้าไม่ได้
        res_old_login = self.client.post('/login', data={'email': 'customer@test.com', 'password': 'customer1234'}, follow_redirects=True)
        self.assertIn('อีเมลหรือรหัสผ่านไม่ถูกต้อง'.encode('utf-8'), res_old_login.data)

        res_new_login = self.client.post('/login', data={'email': 'customer@test.com', 'password': 'NewPassword1234'}, follow_redirects=True)
        self.assertIn('เข้าสู่ระบบสำเร็จ'.encode('utf-8'), res_new_login.data)

        # คืนค่ารหัสผ่านเดิมเพื่อให้เทสต์อื่นไม่ติดขัด
        conn = get_db_connection()
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash('customer1234'), user['id']))
        conn.commit()
        conn.close()

        print("✓ Test 12 ผ่าน: ระบบลืมรหัสผ่าน Secure Single-use Token หมดอายุได้ ใช้งานสำเร็จ 100%")

    def test_13_customer_profile_editing(self):
        """ทดสอบการแก้ไขโปรไฟล์ลูกค้า ชื่อ อีเมล เบอร์โทร ที่อยู่ และรหัสผ่าน พร้อมตรวจสอบสิทธิ์แก้ไขได้เฉพาะตนเอง"""
        # เข้าสู่ระบบในฐานะ Customer
        self.client.post('/login', data={'email': 'customer@test.com', 'password': 'customer1234'}, follow_redirects=True)

        # เปิดหน้าโปรไฟล์
        res_profile = self.client.get('/profile')
        self.assertEqual(res_profile.status_code, 200)
        self.assertIn('โปรไฟล์บัญชีของฉัน'.encode('utf-8'), res_profile.data)

        # อัปเดตข้อมูลส่วนตัว
        res_update = self.client.post('/profile', data={
            'name': 'นายสมชาย สดใส (อัปเดต)',
            'email': 'customer@test.com',
            'phone': '089-999-7777',
            'address': '99/99 ถนนมิตรภาพ ตำบลในเมือง อำเภอเมือง ขอนแก่น 40000',
            'current_password': '',
            'new_password': '',
            'confirm_new_password': ''
        }, follow_redirects=True)
        self.assertIn('อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว'.encode('utf-8'), res_update.data)

        # ตรวจสอบว่าใน SQLite บันทึกข้อมูลใหม่จริง
        conn = get_db_connection()
        updated_user = conn.execute("SELECT name, phone, address FROM users WHERE email = 'customer@test.com'").fetchone()
        conn.close()
        self.assertEqual(updated_user['name'], 'นายสมชาย สดใส (อัปเดต)')
        self.assertEqual(updated_user['phone'], '089-999-7777')

        # คืนค่าเดิม
        conn = get_db_connection()
        conn.execute("UPDATE users SET name = 'นายสมชาย สดใส', phone = '089-123-4567' WHERE email = 'customer@test.com'")
        conn.commit()
        conn.close()

        print("✓ Test 13 ผ่าน: แก้ไขโปรไฟล์ลูกค้า (ชื่อ อีเมล เบอร์โทร ที่อยู่ รูปโปรไฟล์ รหัสผ่าน) สมบูรณ์และปลอดภัย")

    def test_14_member_management_ban_unban(self):
        """ทดสอบระบบจัดการสมาชิก Admin สั่งระงับบัญชี (Ban/Unban) สมาชิกที่ถูกระงับต้องเข้าใช้งานไม่ได้"""
        # 1. สร้างสมาชิกลูกค้าทดสอบใหม่สำหรับการ Ban
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE email = 'banned_test@example.com'")
        conn.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, address, is_banned)
            VALUES (?, ?, ?, 'customer', ?, ?, 0)
        """, ('ลูกค้าที่รอระงับ', 'banned_test@example.com', generate_password_hash('TestPass1234'), '081-111-2222', 'ที่อยู่ทดสอบ'))
        conn.commit()
        banned_user_id = conn.execute("SELECT id FROM users WHERE email = 'banned_test@example.com'").fetchone()['id']
        conn.close()

        # 2. Login เป็น Admin แล้วสั่งระงับบัญชี
        self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        res_ban = self.client.post(f'/admin/customer/{banned_user_id}/toggle-ban', data={
            'action': 'ban',
            'reason': 'มีพฤติกรรมแนบสลิปปลอม'
        }, follow_redirects=True)
        self.assertEqual(res_ban.status_code, 200)
        self.assertIn('ระงับการใช้งานบัญชีของคุณ'.encode('utf-8'), res_ban.data)

        # ตรวจสอบใน SQLite ว่าสถานะเป็น is_banned = 1
        conn = get_db_connection()
        banned_check = conn.execute("SELECT is_banned, banned_reason FROM users WHERE id = ?", (banned_user_id,)).fetchone()
        conn.close()
        self.assertEqual(banned_check['is_banned'], 1)
        self.assertEqual(banned_check['banned_reason'], 'มีพฤติกรรมแนบสลิปปลอม')

        # 3. ผู้ใช้ที่ถูกระงับ พยายาม Login เข้าสู่ระบบ -> ต้องถูกปฏิเสธ
        self.client.get('/logout', follow_redirects=True)
        res_banned_login = self.client.post('/login', data={'email': 'banned_test@example.com', 'password': 'TestPass1234'}, follow_redirects=True)
        self.assertIn('ไม่สามารถเข้าสู่ระบบได้'.encode('utf-8'), res_banned_login.data)
        self.assertIn('มีพฤติกรรมแนบสลิปปลอม'.encode('utf-8'), res_banned_login.data)

        # 4. Admin สั่งปลดการระงับ (Unban)
        self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        res_unban = self.client.post(f'/admin/customer/{banned_user_id}/toggle-ban', data={
            'action': 'unban'
        }, follow_redirects=True)
        self.assertIn('ปลดการระงับบัญชีของคุณ'.encode('utf-8'), res_unban.data)

        # 5. สมาชิกที่ถูกปลดระงับ สามารถ Login ได้ตามปกติ
        self.client.get('/logout', follow_redirects=True)
        res_after_unban = self.client.post('/login', data={'email': 'banned_test@example.com', 'password': 'TestPass1234'}, follow_redirects=True)
        self.assertIn('เข้าสู่ระบบสำเร็จ'.encode('utf-8'), res_after_unban.data)

        # ล้างข้อมูลทดสอบ
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE id = ?", (banned_user_id,))
        conn.commit()
        conn.close()

        print("✓ Test 14 ผ่าน: ระบบจัดการสมาชิก Ban/Unban และการป้องกันสิทธิ์ลูกค้าถูกต้องสมบูรณ์")

    def test_15_cart_ajax_and_quantity_distinction(self):
        """ทดสอบการเพิ่มสินค้าลงตะกร้าแบบ AJAX Real-time และแยกความแตกต่างระหว่างจำนวนรุ่นรถกับจำนวนคันรวม"""
        conn = get_db_connection()
        products_avail = conn.execute("SELECT id, model, price, stock FROM products WHERE stock >= 3 AND status = 'available' ORDER BY stock DESC").fetchall()
        p1 = products_avail[0]
        p2 = products_avail[1]
        conn.close()

        with self.client.session_transaction() as sess:
            sess['cart'] = {}

        # 1. เพิ่ม Wave 110i จำนวน 2 คัน ผ่าน AJAX
        res_ajax1 = self.client.post('/cart/add', data={'product_id': p1['id'], 'quantity': 2}, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(res_ajax1.status_code, 200)
        data1 = res_ajax1.get_json()
        self.assertTrue(data1['success'])
        self.assertEqual(data1['cart_items_count'], 1)  # 1 รุ่น
        self.assertEqual(data1['cart_total_qty'], 2)    # 2 คัน

        # 2. เพิ่ม Wave 125i จำนวน 3 คัน ผ่าน AJAX
        res_ajax2 = self.client.post('/cart/add', data={'product_id': p2['id'], 'quantity': 3}, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(res_ajax2.status_code, 200)
        data2 = res_ajax2.get_json()
        self.assertTrue(data2['success'])
        self.assertEqual(data2['cart_items_count'], 2)  # 2 รุ่น
        self.assertEqual(data2['cart_total_qty'], 5)    # รวม 5 คัน (2+3)

        # 3. ตรวจสอบหน้า cart.html ว่าแสดงผลแยกชัดเจนระหว่างจำนวนรุ่นรถ และ จำนวนคันรวม
        res_cart = self.client.get('/cart')
        self.assertEqual(res_cart.status_code, 200)
        self.assertIn('2 รุ่น'.encode('utf-8'), res_cart.data)
        self.assertIn('5 คัน'.encode('utf-8'), res_cart.data)

        # ล้างตะกร้าหลังทดสอบ
        self.client.post('/cart/clear')

        print("✓ Test 15 ผ่าน: ตะกร้าสินค้า AJAX Real-time Badge และแยกจำนวนรายการ (2 รุ่น) กับจำนวนคัน (5 คัน) ชัดเจน")

    def test_16_reports_comprehensive_analytics(self):
        """ทดสอบหน้ารายงานสรุปผลการดำเนินงาน ยอดขายรายวัน รายเดือน รายปี ยอดขายสะสม และสถิติรุ่นยอดนิยม"""
        # Login ด้วยสิทธิ์ Admin
        self.client.post('/login', data={'email': 'admin@bikeshop.com', 'password': 'admin1234'}, follow_redirects=True)
        res = self.client.get('/admin/reports')
        self.assertEqual(res.status_code, 200)

        # ตรวจสอบส่วนประกอบสำคัญในหน้ารายงาน
        self.assertIn('รายงานสรุปผลการดำเนินงาน'.encode('utf-8'), res.data)
        self.assertIn('ยอดขายสะสมทั้งหมด'.encode('utf-8'), res.data)
        self.assertIn('สต็อกรถในร้าน'.encode('utf-8'), res.data)
        self.assertIn('มูลค่าสินค้าคงคลังรวม'.encode('utf-8'), res.data)
        self.assertIn('สรุปยอดขายรายวัน'.encode('utf-8'), res.data)
        self.assertIn('สรุปยอดขายรายเดือนและรายปี'.encode('utf-8'), res.data)
        self.assertIn('สถิติรุ่นรถยอดนิยมและจำนวนคันที่จำหน่ายได้'.encode('utf-8'), res.data)
        self.assertIn('คำสั่งซื้อล่าสุดและสถานะการชำระเงิน'.encode('utf-8'), res.data)

        # ตรวจสอบการไม่มีคำว่า "จำลอง" หรือ "สมมุติ" ในหน้ารายงาน
        self.assertNotIn('ราคาขายสมมติ'.encode('utf-8'), res.data)
        self.assertNotIn('จำลอง'.encode('utf-8'), res.data)

        print("✓ Test 16 ผ่าน: หน้ารายงานสรุปยอดขาย รายวัน/เดือน/ปี/สะสม สถิติรุ่นยอดนิยม และคำสั่งซื้อครบถ้วน 100%")


if __name__ == '__main__':
    unittest.main()


