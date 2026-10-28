# คู่มือเตรียมตัวนำเสนอโปรเจกต์ (Presentation & Code Explanation Guide)
## โปรเจกต์: เว็บไซต์ร้านขายรถจักรยานยนต์ไม่เกิน 160 cc (MOTO 160 BIKE SHOP)
### สำหรับนักศึกษาชั้นปีที่ 2 สาขาวิชาคอมพิวเตอร์ / วิทยาการคอมพิวเตอร์ / เทคโนโลยีสารสนเทศ

เอกสารนี้สรุปแนวทางการอธิบายโค้ดและสถาปัตยกรรมระบบทั้ง 10 หัวข้อ เพื่อให้นักศึกษาสามารถนำไปตอบคำถามและสาธิตให้อาจารย์ดูได้อย่างมั่นใจ โดยอธิบายจากโค้ดที่ทำงานจริงในโปรเจกต์

---

## 1. ภาพรวมการทำงานของเว็บไซต์ (Architecture Overview)

ระบบทำงานในรูปแบบ **Client-Server Architecture (MVC Pattern - Model-View-Controller)**:
1. **Client (Browser):** ผู้ใช้เปิดเว็บเบราว์เซอร์และส่งคำขอ (HTTP GET/POST Request) ผ่าน URL หรือการกดปุ่มบนฟอร์ม
2. **Server / Controller (Flask Routes):** Flask ทำหน้าที่เป็นเว็บเซิร์ฟเวอร์ รับคำขอ (Request) จากเบราว์เซอร์ แล้วตรวจสอบสิทธิ์ (Authentication & Authorization)
3. **Database / Model (SQLite):** โค้ด Python เรียกใช้คำสั่ง SQL เพื่อสืบค้น (SELECT) หรือแก้ไข (INSERT/UPDATE/DELETE) ข้อมูลในฐานข้อมูล `motorcycle_shop.db`
4. **View / Template Engine (Jinja2):** Flask นำข้อมูลที่ได้จากฐานข้อมูลมาประมวลผลร่วมกับไฟล์ HTML Template แล้ว Render กลับไปเป็นหน้าเว็บ HTML ที่สมบูรณ์ส่งคืนให้เบราว์เซอร์แสดงผล

```text
[ ผู้ใช้งาน / เบราว์เซอร์ ]
        │  ▲
(HTTP Request) │  │ (HTTP Response: HTML/CSS)
        ▼  │
┌──────────────────────────────────────────────┐
│           Flask Backend (app.py)             │
│   ├── routes/auth.py     (ระบบสมาชิก/สิทธิ์)     │
│   ├── routes/shop.py     (หน้าร้าน/ตะกร้า)     │
│   ├── routes/customer.py (สั่งซื้อ/ชำระเงิน)    │
│   └── routes/admin.py    (หลังบ้าน/อนุมัติ)    │
└──────────────┬───────────────────────────────┘
               │  ▲
       (SQL)   │  │ (Rows)
               ▼  │
┌──────────────────────────────────────────────┐
│        SQLite Database (database.py)         │
│          motorcycle_shop.db                  │
└──────────────────────────────────────────────┘
```

---

## 2. หน้าที่ของไฟล์สำคัญในโปรเจกต์

| ชื่อไฟล์ | ตำแหน่ง | หน้าที่หลักและการทำงาน |
| :--- | :--- | :--- |
| `app.py` | Root | จุดเริ่มต้นโปรแกรม (Entry Point), กำหนดค่า Configuration, Secret Key, ลงทะเบียน Blueprints ทั้ง 4 ชุด, และรัน Development Server |
| `database.py` | Root | จัดการการเชื่อมต่อ SQLite (`get_db_connection`), สร้างตาราง (`init_db`), และ Seed ข้อมูลรถตัวอย่าง 20 รุ่น (`seed_db`) |
| `routes/auth.py` | `routes/` | ควบคุมการสมัครสมาชิก (`/register`), เข้าสู่ระบบ (`/login`), ออกจากระบบ (`/logout`), และ Decorators `@login_required`, `@admin_required` |
| `routes/shop.py` | `routes/` | ควบคุมหน้าแรก (`/`), หน้ารายการรถและค้นหา (`/products`), หน้ารายละเอียด (`/product/<id>`), และระบบตะกร้าสินค้าในเซสชัน (`/cart`) |
| `routes/customer.py` | `routes/` | ควบคุมการสั่งซื้อ (`/checkout`), แนบสลิป (`/pay`), ประวัติคำสั่งซื้อ (`/orders`), และดาวน์โหลดใบเสร็จ PDF |
| `routes/admin.py` | `routes/` | ควบคุมแผงควบคุมแอดมิน (`/admin/dashboard`), เพิ่ม/แก้ไข/ลบสินค้า, จัดการสต็อก, ตรวจสอบสลิป, และรายงานยอดขาย |
| `utils/receipt.py` | `utils/` | สร้างเอกสาร PDF ใบเสร็จรับเงินภาษาไทยด้วย ReportLab โดยดึงฟอนต์ Tahoma มาลงทะเบียน |
| `templates/base.html` | `templates/` | แม่แบบหน้าเว็บหลัก (Master Template) มีแถบเมนูนำทาง (Navbar), การแจ้งเตือน (Flash messages) และส่วนท้าย (Footer) |
| `static/css/style.css` | `static/css/` | กำหนดรูปลักษณ์ ดีไซน์สีขาว-ดำ-แดง ปรับการแสดงผลบนมือถือและคอมพิวเตอร์ (Responsive) |

---

## 3. ความแตกต่างระหว่าง Frontend, Backend และ Database

- **Frontend (หน้าบ้าน):**
  - ประกอบด้วย **HTML5**, **CSS3**, และ **Jinja2 Syntax** (`{{ ... }}`, `{% ... %}`)
  - หน้าที่: แสดงผลกราฟิก ข้อความ ฟอร์มกรอกข้อมูล และรับการคลิกจากผู้ใช้
  - อยู่บนเครื่อง Client (เบราว์เซอร์)
- **Backend (หลังบ้าน):**
  - เขียนด้วยภาษา **Python** ทำงานผ่านเฟรมเวิร์ก **Flask**
  - หน้าที่: เป็นสมองกลของระบบ ตรวจสอบความถูกต้องของข้อมูล (Validation), เข้ารหัสรหัสผ่าน, ประมวลผลตรรกะทางธุรกิจ (Business Logic), คำนวณยอดเงิน, และควบคุมสิทธิ์
  - ทำงานบนเซิร์ฟเวอร์ ไม่เปิดเผยโค้ดให้ผู้ใช้เห็นโดยตรง
- **Database (ฐานข้อมูล):**
  - ใช้ **SQLite** (`instance/motorcycle_shop.db`)
  - หน้าที่: แหล่งจัดเก็บข้อมูลระยะยาวอย่างถาวร (Persistent Storage) แม้จะปิดโปรแกรมหรือรีสตาร์ตเครื่อง ข้อมูลผู้ใช้ สินค้า สต็อก และคำสั่งซื้อก็จะไม่สูญหาย

---

## 4. Flask รับข้อมูลจาก HTML Form อย่างไร?

### การส่งข้อมูลจาก HTML:
ที่หน้าเว็บ เช่น `templates/login.html` เรากำหนดแท็ก `<form method="POST">` และระบุชื่อแอตทริบิวต์ `name` ให้กับ Input แต่ละตัว:
```html
<form action="/login" method="POST">
  <input type="email" name="email" required>
  <input type="password" name="password" required>
  <button type="submit">เข้าสู่ระบบ</button>
</form>
```

### การรับข้อมูลใน Flask (`routes/auth.py`):
เมื่อผู้ใช้กด Submit เบราว์เซอร์จะส่ง HTTP POST Request มาที่ Flask เราสามารถดึงค่าได้ผ่านออบเจกต์ `request.form`:
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # Flask อ่านค่าที่ผู้ใช้พิมพ์ส่งมาตามชื่อ name ใน HTML
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    # นำค่า email และ password ไปตรวจสอบต่อกับฐานข้อมูล
```
- กรณีเป็นไฟล์อัปโหลด (เช่น สลิป): จะดึงผ่าน `request.files['slip_file']`

---

## 5. Python ติดต่อ SQLite อย่างไร?

ใน `database.py` เราใช้ไลบรารีมาตรฐาน `sqlite3` ที่มาพร้อมกับ Python:

```python
import sqlite3


def get_db_connection():
  conn = sqlite3.connect('instance/motorcycle_shop.db')
  # กำหนด row_factory เพื่อให้อ่านผลลัพธ์เป็นชื่อคอลัมน์ได้ เช่น row['model']
  conn.row_factory = sqlite3.Row
  # เปิดระบบตรวจ Foreign Key
  conn.execute('PRAGMA foreign_keys = ON;')
  return conn
```

### การป้องกัน SQL Injection:
เราใช้ **Parameterized Queries** โดยใช้เครื่องหมาย `?` เสมอ ห้ามนำตัวแปรมาต่อ String โดยตรง เช่น:
```python
# ปลอดภัย 100% จาก SQL Injection
cursor.execute(
    'SELECT * FROM products WHERE brand = ? AND engine_cc <= ?',
    (brand, max_cc),
)
```

---

## 6. การเพิ่มสินค้าและบันทึกข้อมูลลงฐานข้อมูล

ใน `routes/admin.py` ฟังก์ชัน `product_add()`:

```python
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def product_add():
  if request.method == 'POST':
    code = request.form.get('code')
    model = request.form.get('model')
    engine_cc = request.form.get('engine_cc', type=int)
    price = request.form.get('price', type=float)
    stock = request.form.get('stock', type=int)

    # 1. Backend Validation: ตรวจสอบกฎเหล็กห้ามเกิน 160 cc
    if engine_cc > 160 or engine_cc <= 0:
      flash('ระบบจำกัดเฉพาะรถจักรยานยนต์ความจุไม่เกิน 160 cc เท่านั้น', 'danger')
      return render_template('admin/product_form.html')

    # 2. บันทึกลง SQLite ด้วยคำสั่ง INSERT INTO
    conn = get_db_connection()
    conn.execute(
        """
            INSERT INTO products (code, brand, model, model_year, engine_cc, category, price, stock, description, image_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (code, brand, model, year, engine_cc, category, price, stock, desc, img, status),
    )
    conn.commit()  # บันทึกการเปลี่ยนแปลงถาวร
    conn.close()  # ปิดการเชื่อมต่อ
```

---

## 7. การสมัครสมาชิกและตรวจสอบสิทธิ์ (Authentication & Role Check)

### 7.1 การ Hash รหัสผ่าน (ห้ามเก็บ Plain Text):
ใน `routes/auth.py` เราใช้ `generate_password_hash` จาก Werkzeug:
```python
from werkzeug.security import check_password_hash, generate_password_hash

# ตอนสมัครสมาชิก: แปลง 'customer1234' เป็น Hash ปลอดภัย
password_hash = generate_password_hash(password)
cursor.execute(
    'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
    (name, email, password_hash, 'customer'),
)

# ตอนเข้าสู่ระบบ: ตรวจสอบความถูกต้องโดยไม่ต้องถอดรหัส
user = conn.execute(
    'SELECT * FROM users WHERE email = ?', (email,)
).fetchone()
if user and check_password_hash(user['password_hash'], password):
  session['user_id'] = user['id']
  session['user_role'] = user['role']  # 'admin' หรือ 'customer'
```

### 7.2 การตรวจสอบสิทธิ์ด้วย Decorator:
เราสร้าง `@admin_required` เพื่อป้องกันไม่ให้คนทั่วไปแอบเข้า URL `/admin`:
```python
def admin_required(f):

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get('user_role') != 'admin':
      flash('คุณไม่มีสิทธิ์เข้าถึงหน้าระบบผู้ดูแล', 'danger')
      return redirect(url_for('shop.home'))
    return f(*args, **kwargs)

  return decorated_function
```

---

## 8. การสั่งซื้อและการตัดสต็อก (Database Transaction)

จุดสำคัญที่ทำให้อาจารย์ประทับใจคือ **การใช้ Database Transaction (`commit` และ `rollback`)**:
เมื่อลูกค้ากดสั่งซื้อ หากมีหลายขั้นตอน (ตรวจสต็อก, ตัดสต็อก, สร้างคำสั่งซื้อ, บันทึกรายการสินค้า) ทุกขั้นตอนต้องสำเร็จพร้อมกัน หากขั้นตอนใดล้มเหลว ข้อมูลจะถูกย้อนกลับ (Rollback) ทันที:

```python
try:
  # 1. ตรวจสอบว่าสินค้ามีพอหรือไม่
  for item in checkout_items:
    curr = cursor.execute(
        'SELECT stock FROM products WHERE id = ?', (item['id'],)
    ).fetchone()
    if curr['stock'] < item['quantity']:
      raise ValueError('สต็อกไม่เพียงพอ')

  # 2. บันทึกคำสั่งซื้อหลัก
  cursor.execute(
      'INSERT INTO orders (order_number, user_id, ...) VALUES (...)', (...)
  )
  order_id = cursor.lastrowid

  # 3. ตัดสต็อกสินค้าในตาราง products
  for item in checkout_items:
    cursor.execute(
        """
            UPDATE products 
            SET stock = stock - ?,
                status = CASE WHEN stock - ? <= 0 THEN 'out_of_stock' ELSE status END
            WHERE id = ?
        """,
        (item['quantity'], item['quantity'], item['id']),
    )

  conn.commit()  # ยืนยันว่าทุกขั้นตอนสำเร็จพร้อมกัน
except Exception as e:
  conn.rollback()  # หากเกิด Error ให้ยกเลิกการเปลี่ยนแปลงทั้งหมด คืนค่าเดิม
```

และเมื่อลูกค้าหรือแอดมินกดยกเลิกคำสั่งซื้อ ระบบจะใช้ Transaction ทำการ `UPDATE products SET stock = stock + ?` คืนสต็อกทันที!

---

## 9. การตรวจสอบสลิปและออกใบเสร็จ PDF

### 9.1 แนบสลิปและการป้องกัน:
1. ลูกค้าอัปโหลดไฟล์สลิปผ่านหน้าคำสั่งซื้อ
2. ระบบตรวจนามสกุลไฟล์ (`.png`, `.jpg`, `.jpeg`, `.webp`)
3. บันทึกรูปลง `static/uploads/slips/` และอัปเดตสถานะเป็น `รอตรวจสอบการชำระเงิน`

### 9.2 การอนุมัติโดย Admin:
- แอดมินดูภาพสลิปที่แนบมา
- หากยอดเงินถูกต้อง กด **อนุมัติ**:
  - อัปเดต `payments.status = 'approved'`
  - ปรับสถานะคำสั่งซื้อเป็น `ชำระเงินแล้ว`
  - สร้างเลขที่ใบเสร็จ `receipts.receipt_number`
  - มีเงื่อนไขป้องกันการอนุมัติซ้ำ (Check Double Approval)
- หากยอดไม่ตรง กด **ปฏิเสธ** พร้อมใส่เหตุผล ลูกค้าจะเห็นเหตุผลและสามารถแนบสลิปใหม่ได้

### 9.3 การออกใบเสร็จ PDF ด้วย ReportLab (`utils/receipt.py`):
- ใช้ `SimpleDocTemplate`, `Table`, `Paragraph` จาก ReportLab
- โหลดฟอนต์ **Tahoma (`tahoma.ttf`)** จากโฟลเดอร์ `static/fonts/` เพื่อให้แสดงภาษาไทยได้อย่างถูกต้อง
- สร้างเป็น Stream ในหน่วยความจำ (`io.BytesIO()`) แล้วส่งออกเป็นไฟล์ดาวน์โหลดด้วย `send_file(..., as_attachment=True)`

---

## 10. ลำดับขั้นตอนการสาธิตให้อาจารย์ดู (Step-by-Step Live Demo)

### ขั้นตอนที่ 1: แนะนำหน้าแรกและฟังก์ชันค้นหา (Customer Perspective)
1. เปิดเว็บที่ `http://127.0.0.1:5000`
2. ชี้ให้อาจารย์ดู **แบนเนอร์**, **หมวดหมู่รถ 3 ประเภท**, และ **การ์ดรถ 20 รุ่น**
3. ไปที่เมนู "รถมอเตอร์ไซค์ทั้งหมด"
4. สาธิตการพิมพ์ค้นหา เช่น พิมพ์ `Click` หรือเลือกตัวกรองแบรนด์ `Honda` หรือช่วงความจุ `131 - 160 cc`
5. เน้นย้ำกับอาจารย์ว่า **"ทุกรุ่นมีความจุไม่เกิน 160 cc ตามข้อกำหนดครับ"**

### ขั้นตอนที่ 2: สั่งซื้อและแสดงการตัดสต็อก (Order & Stock Flow)
1. เข้าสู่ระบบด้วยบัญชีลูกค้า: `customer@test.com` / `customer1234`
2. เลือกรถ 1 รุ่น เช่น **Honda Wave 110i** (สังเกตจำนวนสต็อกเดิม เช่น 8 คัน)
3. กดปุ่ม **"ใส่ตะกร้า"** &rarr; ไปที่หน้าตะกร้าสินค้า
4. กด **"ดำเนินการสั่งซื้อ"** &rarr; ยืนยันชื่อ ที่อยู่ เบอร์โทรศัพท์ &rarr; กด **"ยืนยันการสั่งซื้อ"**
5. แสดงให้อาจารย์ดูว่า ระบบสร้างเลขที่คำสั่งซื้อใหม่ (เช่น `ORD-20261013-0001`) และสต็อกรถรุ่นนั้นลดลง 1 คันจริงในฐานข้อมูล

### ขั้นตอนที่ 3: แนบสลิปโอนเงิน
1. ในหน้ารายละเอียดคำสั่งซื้อ จะมีข้อมูลบัญชีธนาคารสำหรับโอนเงิน
2. เลือกไฟล์รูปภาพสลิป &rarr; กด **"อัปโหลดสลิปยืนยันการชำระเงิน"**
3. สถานะคำสั่งซื้อจะเปลี่ยนเป็น **"รอตรวจสอบการชำระเงิน"**

### ขั้นตอนที่ 4: สลับเป็นบทบาท Admin เพื่อตรวจสอบและอนุมัติ
1. กด "ออกจากระบบ" แล้วเข้าสู่ระบบด้วยบัญชีแอดมิน: `admin@bikeshop.com` / `admin1234`
2. ระบบจะพาเข้าสู่ **Admin Dashboard** ทันที ชี้ให้อาจารย์ดูตัวเลขสถิติยอดขายและรายการรอตรวจสลิป
3. คลิกเมนู **"ตรวจสลิปชำระเงิน"**
4. แอดมินดูภาพสลิป แล้วกดปุ่ม **"✓ อนุมัติยอดเงินและออกใบเสร็จ"**
5. แสดงให้อาจารย์ดูว่า สถานะเปลี่ยนเป็น **"ชำระเงินแล้ว"** และปุ่ม **"ดาวน์โหลดใบเสร็จ PDF"** ปรากฏขึ้นมา

### ขั้นตอนที่ 5: ดาวน์โหลดใบเสร็จรับเงิน PDF
1. กดปุ่ม **"ดาวน์โหลดใบเสร็จ PDF"**
2. เปิดไฟล์ PDF ที่ดาวน์โหลดมาให้อาจารย์ดู:
   - มีชื่อร้าน "MOTO 160 BIKE SHOP"
   - เลขที่ใบเสร็จ และเลขที่คำสั่งซื้อ
   - รายละเอียดสินค้า จำนวน และยอดรวมเงิน
   - ตัวอักษรภาษาไทยแสดงผลคมชัดสวยงาม

### ขั้นตอนที่ 6: สาธิตระบบจัดการสินค้า (CRUD) และการป้องกัน CC เกิน 160
1. ไปที่เมนู "จัดการสินค้า (CRUD)" &rarr; กด "+ เพิ่มสินค้ารถใหม่"
2. ลองกรอกรถที่มีความจุ 300 cc (เช่น Forza 300) แล้วกดบันทึก
3. ชี้ให้อาจารย์ดูว่า **ระบบแจ้งเตือนสีแดงและปฏิเสธไม่ยอมให้บันทึก** เพราะมีความจุเกิน 160 cc
4. แสดงการปรับจำนวนสต็อกสินค้าในตารางแบบ Real-Time
