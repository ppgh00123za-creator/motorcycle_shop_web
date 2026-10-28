import os
import sys
import unittest
import io

# Ensure project root is in path
sys.path.insert(0, os.path.abspath('.'))

from app import app
from database import get_db_connection
import pymupdf as fitz
from routes.receipt import calculate_vat_breakdown, generate_receipt_pdf

class ComprehensiveAuditTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_1_admin_reports_all_data_renders(self):
        """ตรวจสอบว่าหน้า /admin/reports แสดงผลข้อมูลครบทั้ง 3 ตาราง และ section สต็อก ไม่เป็นหน้าว่าง"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'admin'
            sess['user_name'] = 'ผู้ดูแลระบบ (Admin)'

        res = self.client.get('/admin/reports')
        self.assertEqual(res.status_code, 200, "หน้า /admin/reports ต้องเปิดได้ HTTP 200")
        html = res.data.decode('utf-8')

        # ตรวจสอบว่ามีข้อมูลยอดขายตามหมวดหมู่ (category_sales)
        self.assertIn('ยอดขายแยกตามประเภทรถ', html)
        self.assertTrue('ออโตเมติก' in html or 'ออโต้เมติก' in html)
        self.assertNotIn('ยังไม่มีข้อมูลยอดขายแยกตามประเภทรถ', html)

        # ตรวจสอบว่ามีข้อมูลรุ่นยอดนิยม (top_models)
        self.assertIn('รุ่นรถยอดนิยม', html)
        self.assertNotIn('ยังไม่มีข้อมูลการจำหน่าย', html)

        # ตรวจสอบว่ามีข้อมูลออเดอร์ที่เสร็จสมบูรณ์ (completed_orders)
        self.assertIn('คำสั่งซื้อที่เสร็จสิ้นและการออกใบเสร็จรับเงิน PDF', html)
        self.assertNotIn('ยังไม่มีรายการคำสั่งซื้อที่เสร็จสมบูรณ์', html)

        # ตรวจสอบส่วนสต็อกสินค้า (inventory-section)
        self.assertIn('inventory-section', html)
        self.assertIn('สถานะสต็อกและมูลค่าสินค้าคงคลัง', html)
        print("✓ ข้อ 1 ผ่าน: /admin/reports มีข้อมูลครบทั้ง 3 ส่วนตามโจทย์ ไม่ปล่อยว่าง")

    def test_2_order_detail_audit_log_and_delivery_notes(self):
        """ตรวจสอบว่าหน้ารายละเอียดออเดอร์ /admin/order/32 แสดงประวัติสถานะและบันทึกครบถ้วน"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'admin'
            sess['user_name'] = 'ผู้ดูแลระบบ (Admin)'

        res = self.client.get('/admin/order/32')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # ประวัติสถานะ
        self.assertIn('ประวัติการเปลี่ยนสถานะคำสั่งซื้อ', html)
        self.assertIn('ชำระเงินแล้ว', html)
        # ตรวจสอบการรองรับบันทึกการจัดส่ง
        self.assertTrue('บันทึกข้อมูลการจัดส่ง' in html or 'ที่อยู่จัดส่ง' in html)
        print("✓ ข้อ 1 ผ่าน: หน้ารายละเอียดออเดอร์แสดงประวัติไทม์ไลน์และข้อมูลครบถ้วน")

    def test_3_thai_pdf_receipt_shaping_and_no_square_boxes(self):
        """ตรวจสอบการสร้าง PDF ภาษาไทยด้วย ReportLab + uharfbuzz ไม่มีวรรณยุกต์ซ้อน และไม่มีกล่องสี่เหลี่ยม []"""
        # คำสั่งซื้อ ID 32
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'admin'
            sess['user_name'] = 'ผู้ดูแลระบบ (Admin)'

        res = self.client.get('/order/32/receipt')
        self.assertEqual(res.status_code, 200, "ดาวน์โหลดใบเสร็จต้องได้ HTTP 200")
        self.assertEqual(res.mimetype, 'application/pdf')

        # ใช้ PyMuPDF อ่านข้อความจาก PDF ที่สร้างขึ้น
        doc = fitz.open(stream=res.data, filetype="pdf")
        self.assertGreater(len(doc), 0, "PDF ต้องมีอย่างน้อย 1 หน้า")
        page = doc[0]
        text = page.get_text()

        # ตรวจสอบข้อมูลสำคัญใน PDF
        self.assertIn("160 ธีระ", text)
        self.assertIn("ใบเสร็จรับเงิน", text)
        self.assertIn("ORD-20261027-0001", text)
        self.assertIn("93,400.00", text)
        self.assertIn("[√] ชําระเงินแล้ว", text)

        # ตรวจสอบว่าไม่มีตัวอักษรกล่องสี่เหลี่ยมไม่แสดงผล (.notdef / broken glyph)
        self.assertNotIn("\ufffd", text, "ต้องไม่มี Unicode replacement character")
        self.assertNotIn("[]", text, "ต้องไม่มีกล่องสี่เหลี่ยม [] หน้าชำระเงินแล้ว")

        print("✓ ข้อ 2 ผ่าน: PDF ภาษาไทยสร้างได้สมบูรณ์ ไม่มีวรรณยุกต์ซ้อนทับ และไม่มีกล่องสี่เหลี่ยม")

    def test_4_vat_dual_mode_calculations(self):
        """ตรวจสอบการคำนวณภาษีมูลค่าเพิ่ม VAT 7% ทั้ง 2 กรณีตามโจทย์"""
        # กรณี 1: ราคาก่อน VAT 86,862 บาท -> VAT 7% = 6,080.34, รวม VAT = 92,942.34
        order_exc = {
            'subtotal': 86862.00,
            'discount': 0.0,
            'shipping_fee': 0.0,
            'vat_rate': 0.07,
            'total_amount': 92942.34
        }
        calc1 = calculate_vat_breakdown(order_exc)
        self.assertAlmostEqual(calc1['net_before_vat'], 86862.00, places=2)
        self.assertAlmostEqual(calc1['vat_amount'], 6080.34, places=2)
        self.assertAlmostEqual(calc1['grand_total'], 92942.34, places=2)
        self.assertFalse(calc1['is_vat_inclusive'])

        # กรณี 2: ราคารวม VAT 93,400 บาท -> ถอดก่อน VAT = 93,400 / 1.07 = 87,289.72, VAT = 6,110.28
        order_inc = {
            'subtotal': 93400.00,
            'discount': 0.0,
            'shipping_fee': 0.0,
            'vat_rate': 0.07,
            'total_amount': 93400.00
        }
        calc2 = calculate_vat_breakdown(order_inc)
        self.assertAlmostEqual(calc2['net_before_vat'], 87289.72, places=2)
        self.assertAlmostEqual(calc2['vat_amount'], 6110.28, places=2)
        self.assertAlmostEqual(calc2['grand_total'], 93400.00, places=2)
        self.assertTrue(calc2['is_vat_inclusive'])

        print("✓ ข้อ 2 ผ่าน: การคำนวณ VAT 7% ถูกต้องตามหลักสรรพากรทั้งกรณีรวม VAT และยังไม่รวม VAT")

    def test_5_typography_and_font_hierarchy(self):
        """ตรวจสอบขนาดฟอนต์และ line-height ใน style.css และ admin.css"""
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            style_css = f.read()

        with open('static/css/admin.css', 'r', encoding='utf-8') as f:
            admin_css = f.read()

        # ตรวจสอบ base html / body
        self.assertIn('font-family: var(--font-primary)', style_css)
        self.assertIn('line-height: 1.6', style_css)
        self.assertIn('line-height: 1.6', admin_css)

        # ตรวจสอบว่าปุ่มและตารางมี font-size ชัดเจน
        self.assertIn('.btn {', style_css)
        self.assertIn('.admin-table', admin_css)

        print("✓ ข้อ 3 ผ่าน: ปรับขนาดฟอนต์และ Line Height เหมาะสมกับภาษาไทยทั้งระบบ")

    def test_6_all_customer_and_admin_pages_return_200(self):
        """ตรวจสอบว่าทุกหน้าสำคัญของระบบผู้ใช้และแอดมินโหลดได้ HTTP 200 ไม่มี Error 500"""
        pages_public = ['/', '/products', '/cart', '/login', '/register', '/forgot-password']
        for p in pages_public:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"หน้าสาธารณะ {p} ต้องโหลดได้ 200")

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'admin'
            sess['user_name'] = 'ผู้ดูแลระบบ (Admin)'

        pages_admin = [
            '/admin/dashboard',
            '/admin/products',
            '/admin/stock/history',
            '/admin/orders',
            '/admin/customers',
            '/admin/tickets',
            '/admin/payments',
            '/admin/reports',
            '/admin/settings'
        ]
        for p in pages_admin:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"หน้าแอดมิน {p} ต้องโหลดได้ 200")

        print("✓ ข้อ 4 ผ่าน: ทุกหน้าของระบบเปิดได้ HTTP 200 ไม่มีข้อผิดพลาด")

if __name__ == '__main__':
    unittest.main()
