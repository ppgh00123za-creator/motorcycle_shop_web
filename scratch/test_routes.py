import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from database import get_db_connection

client = app.test_client()

# Check with admin login (user_id 1 is admin)
with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['role'] = 'admin'
    sess['user_name'] = 'Admin'

print("=== Checking Admin Routes ===")
admin_urls = [
    '/admin/',
    '/admin/dashboard',
    '/admin/orders',
    '/admin/payments',
    '/admin/products',
    '/admin/stock-history',
    '/admin/customers',
    '/admin/reports',
    '/admin/settings',
    '/admin/tickets'
]

for url in admin_urls:
    res = client.get(url)
    print(f"{url} -> status {res.status_code}")
    if res.status_code != 200:
        print(f"  Error or redirect: {res.headers.get('Location')}")

# Check with customer login (user_id 2 or 38 is customer)
conn = get_db_connection()
cust = conn.execute("SELECT id, role, name FROM users WHERE role='customer' LIMIT 1").fetchone()
conn.close()

if cust:
    with client.session_transaction() as sess:
        sess['user_id'] = cust['id']
        sess['role'] = cust['role']
        sess['user_name'] = cust['name']

print("\n=== Checking Customer / Public Routes ===")
public_urls = [
    '/',
    '/products',
    '/cart',
    '/orders',
    '/profile',
    '/customer/tickets',
    '/login',
    '/register',
    '/forgot-password'
]

for url in public_urls:
    res = client.get(url)
    print(f"{url} -> status {res.status_code}")
    if res.status_code != 200:
        print(f"  Error or redirect: {res.headers.get('Location')}")
