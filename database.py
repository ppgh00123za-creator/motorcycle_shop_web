"""
database.py
โมดูลจัดการฐานข้อมูล SQLite สำหรับระบบร้านขายรถจักรยานยนต์
รองรับการเชื่อมต่อ, สร้างตาราง (Schema), และ Seed ข้อมูลตัวอย่างเริ่มต้น
"""

import os
import sqlite3
import sys
from werkzeug.security import generate_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ตำแหน่งของฐานข้อมูล SQLite ในโฟลเดอร์ instance
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'motorcycle_shop.db')


def get_db_connection():
    """สร้างและส่งคืนการเชื่อมต่อฐานข้อมูล SQLite พร้อมคืนค่าแถวแบบชื่อคอลัมน์ (sqlite3.Row)"""
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # เปิดการตรวจสอบ Foreign Key Constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """สร้างตารางที่จำเป็นทั้งหมดหากยังไม่มีในฐานข้อมูล"""
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # ตารางผู้ใช้งาน (users)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer', -- 'admin' หรือ 'customer'
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ตารางสินค้า (products) - จำกัดเฉพาะรถไม่เกิน 160 cc
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        model_year TEXT NOT NULL,
        engine_cc INTEGER NOT NULL CHECK (engine_cc <= 160),
        category TEXT NOT NULL,
        price REAL NOT NULL CHECK (price >= 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
        description TEXT,
        image_url TEXT,
        specs_json TEXT,
        status TEXT NOT NULL DEFAULT 'available', -- 'available', 'out_of_stock', 'discontinued'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ตารางคำสั่งซื้อ (orders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_address TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'รอชำระเงิน',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # ตารางรายการสินค้าในคำสั่งซื้อ (order_items)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_code TEXT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # ตารางการชำระเงินและสลิป (payments)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL UNIQUE,
        slip_image TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
        reject_reason TEXT,
        verified_by INTEGER,
        verified_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (verified_by) REFERENCES users(id)
    );
    """)

    # ตารางประวัติการเปลี่ยนสถานะคำสั่งซื้อ (order_status_history)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        changed_by TEXT DEFAULT 'ระบบ',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    # ตารางเลขที่ใบเสร็จ (receipts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_number TEXT NOT NULL UNIQUE,
        order_id INTEGER NOT NULL UNIQUE,
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    # ตารางคลังคำสั่งซื้อที่จัดเก็บย้อนหลัง (archived_orders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archived_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL UNIQUE,
        order_number TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_address TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        order_created_at TIMESTAMP,
        archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        archive_reason TEXT DEFAULT 'จัดเก็บเข้าคลังประวัติตามนโยบายคงเหลือ 3 ออเดอร์ล่าสุด',
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # ตารางรีเซ็ตรหัสผ่าน (password_resets) ปลอดภัยด้วย Token มีวันหมดอายุและใช้ได้ครั้งเดียว
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # ตารางประวัติการปรับปรุงสต็อก (stock_adjustments)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        old_stock INTEGER NOT NULL,
        new_stock INTEGER NOT NULL,
        change_qty INTEGER NOT NULL,
        reason TEXT NOT NULL,
        admin_id INTEGER,
        admin_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # ตารางแจ้งปัญหาและติดต่อร้าน (support_tickets)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_code TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        subject TEXT NOT NULL,
        details TEXT NOT NULL,
        order_id INTEGER,
        contact_info TEXT,
        status TEXT NOT NULL DEFAULT 'รอตรวจสอบ',
        admin_reply TEXT,
        replied_by INTEGER,
        replied_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # ตารางบันทึกประวัติการระงับและปลดระงับบัญชี (user_ban_logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_ban_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        admin_id INTEGER NOT NULL,
        admin_name TEXT,
        action TEXT NOT NULL,
        reason_category TEXT NOT NULL,
        reason_detail TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # ตรวจสอบและเพิ่มคอลัมน์ให้ตาราง orders หากยังไม่มี
    cursor.execute("PRAGMA table_info(orders);")
    order_columns = [col[1] for col in cursor.fetchall()]
    if 'is_archived' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_archived INTEGER DEFAULT 0;")
    if 'subtotal' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0.0;")
    if 'discount' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN discount REAL DEFAULT 0.0;")
    if 'vat_rate' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN vat_rate REAL DEFAULT 0.07;")
    if 'vat_amount' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN vat_amount REAL DEFAULT 0.0;")
    if 'shipping_method' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN shipping_method TEXT DEFAULT 'pickup';")
    if 'shipping_fee' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN shipping_fee REAL DEFAULT 0.0;")
    if 'is_shipping_estimated' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_shipping_estimated INTEGER DEFAULT 0;")
    if 'delivery_notes' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_notes TEXT;")
    if 'is_restocked' not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_restocked INTEGER DEFAULT 0;")

    # อัปเดตข้อมูลย้อนหลังสำหรับ orders เก่าที่ยังไม่มีค่า subtotal และ vat_amount
    cursor.execute("""
        UPDATE orders 
        SET subtotal = ROUND(total_amount / 1.07, 2),
            vat_amount = ROUND(total_amount - (total_amount / 1.07), 2)
        WHERE (subtotal IS NULL OR subtotal = 0.0) AND total_amount > 0;
    """)

    # ตรวจสอบและเพิ่มคอลัมน์ให้ตาราง users หากยังไม่มี
    cursor.execute("PRAGMA table_info(users);")
    user_cols = [col[1] for col in cursor.fetchall()]
    if 'avatar' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT;")
    if 'is_banned' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0;")
    if 'banned_at' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN banned_at TIMESTAMP;")
    if 'banned_reason' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN banned_reason TEXT;")

    conn.commit()

    # ดำเนินการจัดเก็บประวัติอัตโนมัติให้คงเหลือ 3 ออเดอร์ล่าสุด
    archive_old_completed_orders(conn)

    conn.close()


def seed_db():
    """เพิ่มข้อมูลตัวอย่างเบื้องต้น (ทั้งแอดมิน ลูกค้าทดสอบ และรถ 20 รุ่น) โดยตรวจสอบข้อมูลซ้ำก่อนเพิ่ม"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. ตรวจสอบและเพิ่มผู้ใช้ตั้งต้น (Admin และ Customer ทดสอบ)
    cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@bikeshop.com',))
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin1234')
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('ผู้ดูแลระบบ (Admin)', 'admin@bikeshop.com', admin_hash, 'admin', '081-999-8888', 'สำนักงานใหญ่'))

    cursor.execute("SELECT id FROM users WHERE email = ?", ('customer@test.com',))
    if not cursor.fetchone():
        customer_hash = generate_password_hash('customer1234')
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('นายสมชาย สดใส', 'customer@test.com', customer_hash, 'customer', '089-123-4567', '123/45 ถนนพหลโยธิน แขวงลาดยาว เขตจตุจักร กรุงเทพฯ 10900'))
    else:
        cursor.execute("UPDATE users SET name = 'นายสมชาย สดใส' WHERE email = 'customer@test.com' AND name LIKE '%ลูกค้าตัวอย่าง%'")

    # 2. ข้อมูลรถจักรยานยนต์ 20 รุ่น (ความจุ <= 160 cc ทั้งหมด)
    sample_products = [
        # --- รถครอบครัว (Family) ---
        {
            'code': 'BK-FAM-01',
            'brand': 'Honda',
            'model': 'Wave 110i',
            'model_year': '2024',
            'engine_cc': 109,
            'category': 'ครอบครัว',
            'price': 44400.0,
            'stock': 8,
            'description': 'รถครอบครัวยอดนิยม ประหยัดน้ำมันสูงสุด 76.9 กม./ลิตร เครื่องยนต์ Honda Smart Engine 110 ซีซี ทนทาน คุ้มค่า',
            'image_url': 'wave110i.svg',
            'status': 'available'
        },
        {
            'code': 'BK-FAM-02',
            'brand': 'Honda',
            'model': 'Wave 125i',
            'model_year': '2024',
            'engine_cc': 124,
            'category': 'ครอบครัว',
            'price': 55200.0,
            'stock': 6,
            'description': 'ผู้นำรถครอบครัวระดับพรีเมียม ดีไซน์เรียบหรู เครื่องยนต์ 125 ซีซี ไฟหน้า Full LED พร้อมช่องเก็บของ U-Box ขนาดใหญ่',
            'image_url': 'wave125i.svg',
            'status': 'available'
        },
        {
            'code': 'BK-FAM-03',
            'brand': 'Honda',
            'model': 'Dream 100 รุ่นเก่า',
            'model_year': 'ไม่ทราบปี',
            'engine_cc': 97,
            'category': 'ครอบครัว',
            'price': 28000.0,
            'stock': 0,
            'description': 'รถครอบครัวระดับตำนาน เครื่องยนต์ 100 ซีซี ทนทานสุดคลาสสิก ปัจจุบันเป็นสินค้าสำหรับแค็ตตาล็อกและสะสม (เลิกจำหน่ายอย่างเป็นทางการ)',
            'image_url': 'dream100.svg',
            'status': 'discontinued'
        },
        {
            'code': 'BK-FAM-04',
            'brand': 'Honda',
            'model': 'Super Cub 110',
            'model_year': '2024',
            'engine_cc': 109,
            'category': 'ครอบครัว',
            'price': 48400.0,
            'stock': 5,
            'description': 'สไตล์เรโทรเจแปนนิสคลาสสิก ไฟหน้าทรงกลม LED เครื่องยนต์ 110 ซีซี ขับขี่ง่าย เสน่ห์เหนือกาลเวลา',
            'image_url': 'supercub110.svg',
            'status': 'available'
        },
        {
            'code': 'BK-FAM-05',
            'brand': 'Yamaha',
            'model': 'Finn',
            'model_year': '2024',
            'engine_cc': 114,
            'category': 'ครอบครัว',
            'price': 41200.0,
            'stock': 7,
            'description': 'รถครอบครัวพรีเมียม ประหยัดน้ำมัน รับประกัน 5 ปีไม่จำกัดระยะทาง เครื่องยนต์ 115 ซีซี หัวฉีดอัจฉริยะ',
            'image_url': 'finn.svg',
            'status': 'available'
        },

        # --- รถออโตเมติก (Automatic) ---
        {
            'code': 'BK-AT-01',
            'brand': 'Honda',
            'model': 'Scoopy',
            'model_year': '2024',
            'engine_cc': 109,
            'category': 'ออโตเมติก',
            'price': 49900.0,
            'stock': 10,
            'description': 'แฟชั่นเอ.ที. สุดฮิต ดีไซน์ไอคอนิก ไฟหน้า LED ลายวงแหวน ช่องชาร์จไฟสำรอง USB Type-A',
            'image_url': 'scoopy.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-02',
            'brand': 'Honda',
            'model': 'Click 125i',
            'model_year': '2024',
            'engine_cc': 124,
            'category': 'ออโตเมติก',
            'price': 51900.0,
            'stock': 6,
            'description': 'สปอร์ตเอ.ที. ยอดนิยม ดีไซน์โฉบเฉี่ยวเร้าใจ เครื่องยนต์ eSP 125 ซีซี ระบายความร้อนด้วยน้ำ',
            'image_url': 'click125.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-03',
            'brand': 'Honda',
            'model': 'Click 150i',
            'model_year': '2020',
            'engine_cc': 149,
            'category': 'ออโตเมติก',
            'price': 61200.0,
            'stock': 2,
            'description': 'สปอร์ตเอ.ที. พลัง 150 ซีซี ตัวถังปราดเปรียว อัตราเร่งตอบสนองทันใจ กุญแจสมาร์ทคีย์',
            'image_url': 'click150.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-04',
            'brand': 'Honda',
            'model': 'Click 160',
            'model_year': '2024',
            'engine_cc': 156,
            'category': 'ออโตเมติก',
            'price': 63500.0,
            'stock': 5,
            'description': 'สปอร์ตเอ.ที. รุ่นเรือธง เครื่องยนต์ใหม่ eSP+ 4 วาล์ว 157 ซีซี (พิกัด 156.9 cc ไม่เกิน 160 cc) เบรก ABS ดิสก์เบรกหน้า-หลัง',
            'image_url': 'click160.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-05',
            'brand': 'Honda',
            'model': 'PCX 150 รุ่นเก่า',
            'model_year': '2019',
            'engine_cc': 149,
            'category': 'ออโตเมติก',
            'price': 84500.0,
            'stock': 0,
            'description': 'พรีเมียมเอ.ที. หรูหรา สะดวกสบาย รุ่นก่อนหน้า PCX160 ปัจจุบันเก็บในแค็ตตาล็อกอ้างอิง (เลิกจำหน่ายแล้ว)',
            'image_url': 'pcx150.svg',
            'status': 'discontinued'
        },
        {
            'code': 'BK-AT-06',
            'brand': 'Honda',
            'model': 'PCX 160',
            'model_year': '2024',
            'engine_cc': 156,
            'category': 'ออโตเมติก',
            'price': 93400.0,
            'stock': 4,
            'description': 'ยนตรกรรมพรีเมียมเอ.ที. ระดับไฮเอนด์ เครื่องยนต์ eSP+ 4 วาล์ว ความจุ 156.9 ซีซี ระบบ HSTC ป้องกันล้อหมุนฟรี',
            'image_url': 'pcx160.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-07',
            'brand': 'Honda',
            'model': 'Lead 125',
            'model_year': '2024',
            'engine_cc': 124,
            'category': 'ออโตเมติก',
            'price': 61500.0,
            'stock': 6,
            'description': 'มินิมอลเอ.ที. จุของได้จุใจด้วย U-Box 37 ลิตร เครื่อง eSP+ 4 วาล์ว 125 ซีซี เติมน้ำมันด้านหน้ารถ',
            'image_url': 'lead125.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-08',
            'brand': 'Yamaha',
            'model': 'Fino 115 รุ่นเก่า',
            'model_year': 'ไม่ทราบปี',
            'engine_cc': 113,
            'category': 'ออโตเมติก',
            'price': 32000.0,
            'stock': 0,
            'description': 'รถออโตเมติกแฟชั่นทรงกลมในตำนานยุคบุกเบิก ปัจจุบันเป็นรถสะสมและข้อมูลในแค็ตตาล็อก (เลิกจำหน่ายแล้ว)',
            'image_url': 'fino115.svg',
            'status': 'discontinued'
        },
        {
            'code': 'BK-AT-09',
            'brand': 'Yamaha',
            'model': 'Grand Filano',
            'model_year': '2024',
            'engine_cc': 124,
            'category': 'ออโตเมติก',
            'price': 64700.0,
            'stock': 8,
            'description': 'ออโตเมติกพรีเมียมแฟชั่น เครื่องยนต์บลูคอร์ไฮบริด 125 ซีซี ประหยัดน้ำมัน ไฟ Full LED ดีไซน์สไตล์ยุโรป',
            'image_url': 'grandfilano.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-10',
            'brand': 'Yamaha',
            'model': 'Aerox 155',
            'model_year': '2024',
            'engine_cc': 155,
            'category': 'ออโตเมติก',
            'price': 72500.0,
            'stock': 4,
            'description': 'สปอร์ตเอ.ที. อัจฉริยะ เครื่องยนต์บลูคอร์ 155 ซีซี วาล์วแปรผัน VVA เชื่อมต่อแอป Y-Connect ได้',
            'image_url': 'aerox155.svg',
            'status': 'available'
        },
        {
            'code': 'BK-AT-11',
            'brand': 'Yamaha',
            'model': 'NMAX 155',
            'model_year': '2024',
            'engine_cc': 155,
            'category': 'ออโตเมติก',
            'price': 92900.0,
            'stock': 5,
            'description': 'พรีเมียมเอ.ที. สไตล์แม็กซี่ เครื่องยนต์บลูคอร์ 155 ซีซี VVA ดิสก์เบรกหน้า-หลัง พร้อมระบบ Dual ABS และ TCS',
            'image_url': 'nmax155.svg',
            'status': 'available'
        },

        # --- รถสปอร์ตและรถขนาดเล็ก (Sport & Mini) ---
        {
            'code': 'BK-SPT-01',
            'brand': 'Honda',
            'model': 'MSX 125',
            'model_year': '2021',
            'engine_cc': 124,
            'category': 'สปอร์ต/มินิ',
            'price': 71000.0,
            'stock': 3,
            'description': 'มินิสตรีทไบค์สุดคล่องตัว เกียร์คลัตช์มือ 5 สปีด โช้กหน้าหัวกลับ Upside Down ขี่สนุก คล่องตัวในเมือง',
            'image_url': 'msx125.svg',
            'status': 'available'
        },
        {
            'code': 'BK-SPT-02',
            'brand': 'Honda',
            'model': 'CBR150R',
            'model_year': '2024',
            'engine_cc': 149,
            'category': 'สปอร์ต/มินิ',
            'price': 99900.0,
            'stock': 3,
            'description': 'เรซซิ่งสปอร์ตสายพันธุ์แชมป์ เครื่องยนต์ DOHC 4 วาล์ว 150 ซีซี ระบายความร้อนด้วยน้ำ สลิปเปอร์คลัตช์ Assist Slipper Clutch',
            'image_url': 'cbr150r.svg',
            'status': 'available'
        },
        {
            'code': 'BK-SPT-03',
            'brand': 'Yamaha',
            'model': 'R15',
            'model_year': '2024',
            'engine_cc': 155,
            'category': 'สปอร์ต/มินิ',
            'price': 118000.0,
            'stock': 3,
            'description': 'สปอร์ตเรซซิ่งระดับท็อป 155 ซีซี VVA เฟรม Deltabox โช้กหน้าหัวกลับ สลิปเปอร์คลัตช์ แฟริ่งแอโรไดนามิกระดับพรีเมียม',
            'image_url': 'r15.svg',
            'status': 'available'
        },
        {
            'code': 'BK-SPT-04',
            'brand': 'Suzuki',
            'model': 'Raider R150',
            'model_year': '2023',
            'engine_cc': 147,
            'category': 'สปอร์ต/มินิ',
            'price': 69900.0,
            'stock': 2,
            'description': 'ไฮเปอร์อันเดอร์โบน เครื่องยนต์ทวินแคม DOHC 4 วาล์ว 150 ซีซี ระบายความร้อนด้วยน้ำ น้ำหนักเบา อัตราเร่งจัดจ้าน',
            'image_url': 'raider150.svg',
            'status': 'available'
        }
    ]

    # 2. ตรวจสอบและเพิ่มข้อมูลสินค้าตัวอย่างหากตารางยังว่างเปล่า
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        for p in sample_products:
            cursor.execute("""
                INSERT INTO products (code, brand, model, model_year, engine_cc, category, price, stock, description, image_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (p['code'], p['brand'], p['model'], p['model_year'], p['engine_cc'], p['category'], p['price'], p['stock'], p['description'], p['image_url'], p['status']))

    # 3. ซิงค์เส้นทางรูปภาพต้นฉบับจริงจากโฟลเดอร์ รูปภาพ/รถมอเตอร์ไซค์
    try:
        from config import PRODUCT_IMAGE_MAP
        for model_name, img_path in PRODUCT_IMAGE_MAP.items():
            cursor.execute("UPDATE products SET image_url = ? WHERE model = ?", (img_path, model_name))
    except Exception as e:
        print(f"Warning: could not sync PRODUCT_IMAGE_MAP: {e}")

    # 4. ซิงค์รายละเอียดสเปกทางเทคนิคครบทั้ง 20 รุ่น (specs_json)
    try:
        import json
        from specs_data import MOTORCYCLE_SPECS
        for code, spec in MOTORCYCLE_SPECS.items():
            cursor.execute("UPDATE products SET specs_json = ? WHERE code = ?", (json.dumps(spec, ensure_ascii=False), code))
    except Exception as e:
        print(f"Warning: could not sync MOTORCYCLE_SPECS: {e}")

    conn.commit()
    conn.close()


def log_order_status(conn, order_id, status, notes=None, changed_by='ระบบ'):
    """ฟังก์ชันส่วนกลางสำหรับบันทึกประวัติการเปลี่ยนสถานะคำสั่งซื้อลงฐานข้อมูล"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO order_status_history (order_id, status, notes, changed_by)
        VALUES (?, ?, ?, ?)
    """, (order_id, status, notes, changed_by))


def archive_old_completed_orders(conn=None, keep_limit=3):
    """
    จัดเก็บคำสั่งซื้อที่เสร็จสิ้นแล้ว ('ชำระเงินแล้ว', 'จัดส่งแล้ว') ให้คงเหลือแสดงในระบบหลักเพียง 3 ออเดอร์ล่าสุด
    ออเดอร์ที่เก่ากว่าจะถูกทำเครื่องหมาย is_archived = 1 และบันทึกเข้าตาราง archived_orders อย่างปลอดภัย
    โดยไม่ลบข้อมูล Foreign Keys ใน order_items, payments, receipts, order_status_history
    และไม่กระทบสต็อกสินค้า
    """
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cursor = conn.cursor()
    try:
        # ตรวจสอบว่าคอลัมน์ is_archived มีอยู่หรือยัง
        cursor.execute("PRAGMA table_info(orders);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'is_archived' not in cols:
            cursor.execute("ALTER TABLE orders ADD COLUMN is_archived INTEGER DEFAULT 0;")

        # ดึงออเดอร์ที่เสร็จสิ้นทั้งหมด เรียงจากใหม่ไปเก่า (id DESC)
        cursor.execute("""
            SELECT id, order_number, user_id, customer_name, customer_phone, customer_address, 
                   total_amount, status, created_at, is_archived
            FROM orders
            WHERE status IN ('ชำระเงินแล้ว', 'จัดส่งแล้ว')
            ORDER BY id DESC
        """)
        completed_orders = cursor.fetchall()

        # 3 ออเดอร์แรก (ล่าสุด) ให้คงสถานะ is_archived = 0
        keep_orders = completed_orders[:keep_limit]
        for ord_row in keep_orders:
            if ord_row['is_archived'] != 0:
                cursor.execute("UPDATE orders SET is_archived = 0 WHERE id = ?", (ord_row['id'],))
                cursor.execute("DELETE FROM archived_orders WHERE order_id = ?", (ord_row['id'],))

        # ออเดอร์ที่เก่ากว่า 3 รายการล่าสุด จะถูกจัดเก็บเข้าคลังประวัติ (Archive)
        archive_candidates = completed_orders[keep_limit:]
        for ord_row in archive_candidates:
            if ord_row['is_archived'] != 1:
                cursor.execute("UPDATE orders SET is_archived = 1 WHERE id = ?", (ord_row['id'],))
                cursor.execute("""
                    INSERT OR IGNORE INTO archived_orders (
                        order_id, order_number, user_id, customer_name, customer_phone, customer_address,
                        total_amount, status, order_created_at, archive_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ord_row['id'], ord_row['order_number'], ord_row['user_id'], ord_row['customer_name'],
                    ord_row['customer_phone'], ord_row['customer_address'], ord_row['total_amount'],
                    ord_row['status'], ord_row['created_at'], 'จัดเก็บเข้าคลังประวัติตามนโยบายคงเหลือ 3 ออเดอร์ล่าสุด'
                ))
                log_order_status(conn, ord_row['id'], ord_row['status'], 
                                 'จัดเก็บเข้าคลังประวัติ (Archived) ตามนโยบายเก็บ 3 ออเดอร์ล่าสุด', 
                                 'ระบบอัตโนมัติ')

        # จัดการออเดอร์ที่ยกเลิกเก่าเกิน 3 รายการล่าสุดด้วยเพื่อความสะอาดและเป็นระเบียบ
        cursor.execute("""
            SELECT id, order_number, user_id, customer_name, customer_phone, customer_address, 
                   total_amount, status, created_at, is_archived
            FROM orders
            WHERE status = 'ยกเลิก'
            ORDER BY id DESC
        """)
        cancelled_orders = cursor.fetchall()
        for ord_row in cancelled_orders[:keep_limit]:
            if ord_row['is_archived'] != 0:
                cursor.execute("UPDATE orders SET is_archived = 0 WHERE id = ?", (ord_row['id'],))
        for ord_row in cancelled_orders[keep_limit:]:
            if ord_row['is_archived'] != 1:
                cursor.execute("UPDATE orders SET is_archived = 1 WHERE id = ?", (ord_row['id'],))
                cursor.execute("""
                    INSERT OR IGNORE INTO archived_orders (
                        order_id, order_number, user_id, customer_name, customer_phone, customer_address,
                        total_amount, status, order_created_at, archive_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ord_row['id'], ord_row['order_number'], ord_row['user_id'], ord_row['customer_name'],
                    ord_row['customer_phone'], ord_row['customer_address'], ord_row['total_amount'],
                    ord_row['status'], ord_row['created_at'], 'จัดเก็บเข้าคลังประวัติคำสั่งซื้อที่ยกเลิกเก่า'
                ))

        conn.commit()
    finally:
        if close_conn:
            conn.close()


if __name__ == '__main__':
    print("กำลังสร้างและเริ่มต้นฐานข้อมูล...")
    init_db()
    seed_db()
    print("สร้างฐานข้อมูลและเพิ่มข้อมูลตัวอย่าง 20 รุ่นสำเร็จเรียบร้อย!")
