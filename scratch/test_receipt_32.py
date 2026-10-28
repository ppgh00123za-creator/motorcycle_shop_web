import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection
from routes.receipt import generate_receipt_pdf
import fitz

conn = get_db_connection()
order = conn.execute("SELECT * FROM orders WHERE id = 32").fetchone()
items = conn.execute("SELECT * FROM order_items WHERE order_id = 32").fetchall()
payment = conn.execute("SELECT * FROM payments WHERE order_id = 32").fetchone()
conn.close()

pdf_buf = generate_receipt_pdf(order, items, 'REC-20261027-0001', payment)
with open('scratch/receipt_32_current.pdf', 'wb') as f:
    f.write(pdf_buf.getvalue())

# Render to PNG
doc = fitz.open('scratch/receipt_32_current.pdf')
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save('scratch/receipt_32_current.png')
print("Rendered current receipt to scratch/receipt_32_current.png")
