import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from database import get_db_connection

client = app.test_client()

# Login as admin
with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['user_role'] = 'admin'
    sess['user_name'] = 'Admin'

conn = get_db_connection()
order_ids = [r['id'] for r in conn.execute("SELECT id FROM orders LIMIT 5").fetchall()]
product_ids = [r['id'] for r in conn.execute("SELECT id FROM products LIMIT 5").fetchall()]
customer_ids = [r['id'] for r in conn.execute("SELECT id FROM users WHERE role='customer' LIMIT 5").fetchall()]
ticket_ids = [r['id'] for r in conn.execute("SELECT id FROM support_tickets LIMIT 5").fetchall()]
conn.close()

admin_routes = [
    '/admin/',
    '/admin/dashboard',
    '/admin/orders',
    '/admin/payments',
    '/admin/products',
    '/admin/products/add',
    '/admin/stock',
    '/admin/stock/history',
    '/admin/customers',
    '/admin/reports',
    '/admin/settings',
    '/admin/tickets',
]

for oid in order_ids:
    admin_routes.append(f'/admin/order/{oid}')
for pid in product_ids:
    admin_routes.append(f'/admin/products/edit/{pid}')
for cid in customer_ids:
    admin_routes.append(f'/admin/customer/{cid}')
    admin_routes.append(f'/admin/customer/{cid}/ban')
for tid in ticket_ids:
    admin_routes.append(f'/admin/ticket/{tid}')

print("=== Testing Admin Routes ===")
for url in admin_routes:
    res = client.get(url)
    if res.status_code != 200:
        print(f"FAILED {url}: status={res.status_code}")
    else:
        # Check if reports or other page has empty indicator
        text = res.get_data(as_text=True)
        if 'ไม่มีข้อมูล' in text or 'ยังไม่มี' in text:
            print(f"EMPTY STATE in {url}")
        else:
            print(f"OK {url}")

print("\n=== Testing Customer Routes ===")
# Switch to customer
with client.session_transaction() as sess:
    sess['user_id'] = 1  # user 1 has orders in DB as well
    sess['user_role'] = 'customer'
    sess['user_name'] = 'Customer'

customer_routes = [
    '/',
    '/products',
    '/cart',
    '/orders',
    '/profile',
    '/tickets',
]
for oid in order_ids:
    customer_routes.append(f'/order/{oid}')
    customer_routes.append(f'/order/{oid}/receipt')
for pid in product_ids:
    customer_routes.append(f'/product/{pid}')
for tid in ticket_ids:
    customer_routes.append(f'/ticket/{tid}')

for url in customer_routes:
    res = client.get(url)
    if res.status_code != 200:
        print(f"FAILED {url}: status={res.status_code}")
    else:
        text = res.get_data(as_text=True)
        if 'ไม่มีข้อมูล' in text or 'ยังไม่มี' in text:
            print(f"EMPTY STATE in {url}")
        else:
            print(f"OK {url}")
