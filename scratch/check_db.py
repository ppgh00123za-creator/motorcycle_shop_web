import sqlite3
import sys

# Set stdout encoding
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('instance/motorcycle_shop.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Schema of payments table:")
for col in cursor.execute("PRAGMA table_info(payments)").fetchall():
    print(f"  {col['name']} ({col['type']})")

print("\nSchema of orders table:")
for col in cursor.execute("PRAGMA table_info(orders)").fetchall():
    print(f"  {col['name']} ({col['type']})")

print("\nSchema of receipts table:")
for col in cursor.execute("PRAGMA table_info(receipts)").fetchall():
    print(f"  {col['name']} ({col['type']})")

print("\nDistinct order statuses:")
for r in cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status").fetchall():
    print(f"  {r[0]}: {r[1]}")

print("\nPayments (last 5):")
for r in cursor.execute("SELECT * FROM payments ORDER BY id DESC LIMIT 5").fetchall():
    print(dict(r))
