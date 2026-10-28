import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from routes.receipt import generate_receipt_pdf

# Case 1: VAT Inclusive (93,400)
order_inc = {
    'order_number': 'ORD-TEST-01',
    'created_at': '2026-10-27 10:00:00',
    'customer_name': 'นายทดสอบ รวมแวต',
    'customer_phone': '0812345678',
    'customer_address': 'กรุงเทพฯ',
    'shipping_method': 'pickup',
    'delivery_notes': None,
    'status': 'ชำระเงินแล้ว',
    'subtotal': 93400.0,
    'discount': 0.0,
    'vat_rate': 0.07,
    'vat_amount': 6110.28,
    'shipping_fee': 0.0,
    'total_amount': 93400.0
}
items = [{
    'product_code': 'TEST-01',
    'product_name': 'Honda PCX 160',
    'quantity': 1,
    'price': 93400.0,
    'subtotal': 93400.0
}]

pdf1 = generate_receipt_pdf(order_inc, items, 'REC-TEST-01')
assert len(pdf1.getvalue()) > 1000
print("✓ Case 1 Passed: VAT Inclusive (93,400.00)")

# Case 2: VAT Exclusive (86,862) -> VAT 6,080.34 -> Total 92,942.34
order_exc = {
    'order_number': 'ORD-TEST-02',
    'created_at': '2026-10-27 10:00:00',
    'customer_name': 'นายทดสอบ ก่อนแวต',
    'customer_phone': '0898765432',
    'customer_address': 'ขอนแก่น',
    'shipping_method': 'pickup',
    'delivery_notes': None,
    'status': 'ชำระเงินแล้ว',
    'subtotal': 86862.0,
    'discount': 0.0,
    'vat_rate': 0.07,
    'vat_amount': 6080.34,
    'shipping_fee': 0.0,
    'total_amount': 92942.34
}
pdf2 = generate_receipt_pdf(order_exc, items, 'REC-TEST-02')
assert len(pdf2.getvalue()) > 1000
print("✓ Case 2 Passed: VAT Exclusive (86,862.00 -> VAT 6,080.34 -> Total 92,942.34)")
