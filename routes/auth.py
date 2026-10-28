"""
routes/auth.py
ระบบจัดการผู้ใช้ การสมัครสมาชิก เข้าสู่ระบบ ออกจากระบบ และ Decorator ตรวจสอบสิทธิ์
"""

import re
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)


def validate_password_strength(password):
    """
    ตรวจสอบความปลอดภัยของรหัสผ่านตามข้อกำหนด:
    - ความยาวอย่างน้อย 8 ตัวอักษร
    - ต้องมีทั้งตัวอักษรภาษาอังกฤษ ([a-zA-Z]) และตัวเลข ([0-9])
    - แนะนำให้ผสมตัวพิมพ์ใหญ่ พิมพ์เล็ก และอักขระพิเศษ
    """
    if not password or len(password) < 8:
        return False, 'รหัสผ่านไม่ปลอดภัย กรุณาใช้รหัสผ่านอย่างน้อย 8 ตัวอักษร และมีทั้งตัวอักษรภาษาอังกฤษกับตัวเลข'
    
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return False, 'รหัสผ่านไม่ปลอดภัย กรุณาใช้รหัสผ่านอย่างน้อย 8 ตัวอักษร และมีทั้งตัวอักษรภาษาอังกฤษกับตัวเลข'
        
    return True, ''


def login_required(f):
    """Decorator ตรวจสอบว่าผู้ใช้เข้าสู่ระบบแล้วหรือยัง และไม่ถูกระงับการใช้งาน"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('กรุณาเข้าสู่ระบบก่อนทำรายการ', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        conn = get_db_connection()
        user = conn.execute("SELECT is_banned, banned_reason FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()

        if user and user['is_banned']:
            session.clear()
            reason = user['banned_reason'] or 'บัญชีของท่านถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ'
            flash(f'บัญชีของคุณถูกระงับการใช้งาน: {reason}', 'danger')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator ตรวจสอบสิทธิ์ผู้ดูแลระบบ (Admin) ฝั่งเซิร์ฟเวอร์ทุกครั้ง"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('กรุณาเข้าสู่ระบบด้วยบัญชีผู้ดูแลระบบ', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('คุณไม่มีสิทธิ์เข้าถึงหน้าระบบผู้ดูแล', 'danger')
            return redirect(url_for('shop.home'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """หน้าสมัครสมาชิกใหม่"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        # ตรวจสอบความถูกต้องของข้อมูล
        if not name or not email or not password:
            flash('กรุณากรอกชื่อ อีเมล และรหัสผ่านให้ครบถ้วน', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)

        is_valid_pw, pw_err_msg = validate_password_strength(password)
        if not is_valid_pw:
            flash(pw_err_msg, 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)

        if password != confirm_password:
            flash('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)

        conn = get_db_connection()
        # ตรวจสอบอีเมลซ้ำ
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            conn.close()
            flash('อีเมลนี้ถูกใช้งานแล้ว กรุณาใช้อีเมลอื่นหรือเข้าสู่ระบบ', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)

        # บันทึกรหัสผ่านด้วย Hash (ห้ามบันทึกเป็นข้อความธรรมดา)
        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, address)
            VALUES (?, ?, ?, 'customer', ?, ?)
        """, (name, email, password_hash, phone, address))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # เข้าสู่ระบบอัตโนมัติหลังสมัครเสร็จ
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_role'] = 'customer'

        flash(f'สมัครสมาชิกสำเร็จ! ยินดีต้อนรับคุณ {name}', 'success')
        return redirect(url_for('shop.home'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """หน้าเข้าสู่ระบบ พร้อมตรวจสอบสถานะการระงับบัญชี (Ban)"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_url = request.form.get('next') or request.args.get('next')

        if not email or not password:
            flash('กรุณากรอกอีเมลและรหัสผ่าน', 'danger')
            return render_template('login.html', email=email)

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            # ตรวจสอบว่าบัญชีถูกระงับการใช้งานหรือไม่
            if user['is_banned']:
                reason = user['banned_reason'] or 'บัญชีของท่านถูกระงับการใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ'
                flash(f'ไม่สามารถเข้าสู่ระบบได้: {reason}', 'danger')
                return render_template('login.html', email=email)

            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']

            flash(f'เข้าสู่ระบบสำเร็จ ยินดีต้อนรับคุณ {user["name"]}', 'success')

            if user['role'] == 'admin':
                return redirect(next_url or url_for('admin.dashboard'))
            return redirect(next_url or url_for('shop.home'))
        else:
            flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """ออกจากระบบและล้างเซสชัน"""
    session.clear()
    flash('ออกจากระบบเรียบร้อยแล้ว แล้วพบกันใหม่!', 'info')
    return redirect(url_for('shop.home'))


# ================== ระบบลืมรหัสผ่าน (Forgot & Reset Password) ==================

def send_reset_email(to_email, reset_url):
    """ส่งอีเมลรีเซ็ตรหัสผ่านผ่าน SMTP หากเปิดใช้งาน"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS, MAIL_FROM, SHOP_CONFIG

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False, "ยังไม่ได้ตั้งค่า SMTP_USERNAME และ SMTP_PASSWORD ในไฟล์ .env"

    subject = f"รีเซ็ตรหัสผ่านบัญชีร้าน {SHOP_CONFIG['name']}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #ffffff;">
        <h2 style="color: #da291c; margin-top: 0;">ร้าน {SHOP_CONFIG['name']}</h2>
        <p style="font-size: 15px; color: #1f2937;">เรียน คุณลูกค้า,</p>
        <p style="font-size: 14px; color: #4b5563; line-height: 1.6;">
            เราได้รับคำขอรีเซ็ตรหัสผ่านสำหรับบัญชีที่ผูกกับอีเมลนี้ กรุณาคลิกปุ่มด้านล่างเพื่อดำเนินการตั้งรหัสผ่านใหม่:
        </p>
        <div style="margin: 30px 0; text-align: center;">
            <a href="{reset_url}" style="background-color: #da291c; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 15px;">
                ตั้งรหัสผ่านใหม่
            </a>
        </div>
        <p style="font-size: 13px; color: #6b7280; line-height: 1.5;">
            หรือคัดลอกลิงก์นี้ไปวางในเบราว์เซอร์ของคุณ:<br>
            <a href="{reset_url}" style="color: #da291c; word-break: break-all;">{reset_url}</a>
        </p>
        <hr style="border: none; border-top: 1px solid #f3f4f6; margin: 24px 0;">
        <p style="font-size: 12px; color: #9ca3af; line-height: 1.4;">
            * ลิงก์นี้มีความปลอดภัย ใช้งานได้เพียง 1 ครั้ง และจะหมดอายุภายใน 1 ชั่วโมง<br>
            หากท่านไม่ได้เป็นผู้ส่งคำขอนี้ สามารถเพิกเฉยต่ออีเมลฉบับนี้ได้อย่างปลอดภัย
        </p>
    </div>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        if SMTP_USE_TLS:
            server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(MAIL_FROM, [to_email], msg.as_string())
        server.quit()
        return True, "ส่งอีเมลสำเร็จ"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการเชื่อมต่อ SMTP: {str(e)}"


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """หน้าขอลิงก์รีเซ็ตรหัสผ่านผ่านอีเมล พร้อมสร้าง Token ปลอดภัยที่หมดอายุได้"""
    import secrets
    from datetime import datetime, timedelta

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('กรุณากรอกอีเมลของคุณ', 'danger')
            return render_template('forgot_password.html')

        conn = get_db_connection()
        user = conn.execute("SELECT id, name, email, is_banned FROM users WHERE email = ?", (email,)).fetchone()

        if not user:
            conn.close()
            # เพื่อความปลอดภัย ไม่ควรเปิดเผยว่ามีอีเมลนี้อยู่ในระบบหรือไม่ แต่แสดงข้อความสำเร็จ
            flash('หากอีเมลนี้มีอยู่ในระบบ เราได้ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปแล้ว กรุณาตรวจสอบกล่องจดหมายของคุณ', 'info')
            return redirect(url_for('auth.login'))

        if user['is_banned']:
            conn.close()
            flash('ไม่สามารถรีเซ็ตรหัสผ่านได้เนื่องจากบัญชีนี้ถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ', 'danger')
            return render_template('forgot_password.html', email=email)

        # สร้าง Secure Token แบบ URL-Safe
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO password_resets (user_id, token, expires_at, used)
            VALUES (?, ?, ?, 0)
        """, (user['id'], token, expires_at))
        conn.commit()
        conn.close()

        reset_url = url_for('auth.reset_password', token=token, _external=True)
        email_sent, email_msg = send_reset_email(email, reset_url)

        if email_sent:
            flash('เราได้ส่งลิงก์รีเซ็ตรหัสผ่านไปยังอีเมลของคุณเรียบร้อยแล้ว (ลิงก์มีอายุ 1 ชั่วโมง)', 'success')
        else:
            # หาก SMTP ยังไม่ได้ตั้งค่าหรือเกิดข้อผิดพลาดในสภาพแวดล้อม Dev/Local ให้แสดงลิงก์อำนวยความสะดวก
            flash(f'สร้างลิงก์รีเซ็ตรหัสผ่านสำเร็จ (SMTP: {email_msg}) สามารถใช้ลิงก์นี้ได้ทันที: {reset_url}', 'info')

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """หน้าตั้งรหัสผ่านใหม่ด้วย Token ที่ปลอดภัยและยังไม่หมดอายุ"""
    from datetime import datetime

    conn = get_db_connection()
    reset_record = conn.execute("""
        SELECT pr.*, u.email, u.name 
        FROM password_resets pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.token = ?
    """, (token,)).fetchone()

    if not reset_record:
        conn.close()
        flash('ลิงก์รีเซ็ตรหัสผ่านไม่ถูกต้อง หรือไม่พบในระบบ', 'danger')
        return redirect(url_for('auth.forgot_password'))

    # ตรวจสอบว่าถูกใช้ไปแล้วหรือไม่
    if reset_record['used']:
        conn.close()
        flash('ลิงก์นี้ถูกใช้งานไปแล้ว กรุณาขอลิงก์ใหม่', 'warning')
        return redirect(url_for('auth.forgot_password'))

    # ตรวจสอบวันหมดอายุ (1 ชั่วโมง)
    expires_at = reset_record['expires_at']
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except Exception:
            pass

    if isinstance(expires_at, datetime) and datetime.now() > expires_at:
        conn.close()
        flash('ลิงก์รีเซ็ตรหัสผ่านนี้หมดอายุแล้ว (มีอายุ 1 ชั่วโมง) กรุณาขอใหม่อีกครั้ง', 'warning')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        is_valid_pw, pw_err_msg = validate_password_strength(password)
        if not is_valid_pw:
            conn.close()
            flash(pw_err_msg, 'danger')
            return render_template('reset_password.html', token=token, email=reset_record['email'])

        if password != confirm_password:
            conn.close()
            flash('รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน', 'danger')
            return render_template('reset_password.html', token=token, email=reset_record['email'])

        # แฮชรหัสผ่านใหม่และอัปเดตลงตาราง users
        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, reset_record['user_id']))
        # มาร์ก Token ว่าใช้งานแล้ว (Single-use)
        cursor.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_record['id'],))
        conn.commit()
        conn.close()

        flash('ตั้งรหัสผ่านใหม่เรียบร้อยแล้ว! กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่ของคุณ', 'success')
        return redirect(url_for('auth.login'))

    conn.close()
    return render_template('reset_password.html', token=token, email=reset_record['email'])


# ================== แก้ไขโปรไฟล์ลูกค้า (Customer Profile) ==================

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """หน้าดูและแก้ไขข้อมูลส่วนตัวของลูกค้า (แก้ได้เฉพาะบัญชีตนเองเท่านั้น)"""
    import os, time
    from routes.helpers import allowed_file

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    if not user:
        conn.close()
        session.clear()
        flash('ไม่พบข้อมูลบัญชีผู้ใช้ กรุณาเข้าสู่ระบบใหม่', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')

        if not name or not email:
            conn.close()
            flash('กรุณากรอกชื่อและอีเมล', 'danger')
            return render_template('profile.html', user=user)

        # ตรวจสอบอีเมลซ้ำกับผู้อื่น
        dup = conn.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, session['user_id'])).fetchone()
        if dup:
            conn.close()
            flash('อีเมลนี้มีผู้ใช้งานอื่นในระบบแล้ว กรุณาใช้อีเมลอื่น', 'danger')
            return render_template('profile.html', user=user)

        avatar_filename = user['avatar']

        # จัดการอัปโหลดรูปโปรไฟล์
        if 'avatar_file' in request.files:
            avatar_file = request.files['avatar_file']
            if avatar_file and avatar_file.filename != '':
                if not allowed_file(avatar_file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
                    conn.close()
                    flash('อนุญาตเฉพาะไฟล์รูปภาพ .png, .jpg, .jpeg, .webp เท่านั้น', 'danger')
                    return render_template('profile.html', user=user)

                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                avatar_dir = os.path.join(base_dir, 'static', 'ไฟล์ที่ผู้ใช้อัปโหลด', 'avatars')
                os.makedirs(avatar_dir, exist_ok=True)

                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                avatar_filename = f"avatar_{session['user_id']}_{int(time.time())}.{ext}"
                avatar_path = os.path.join(avatar_dir, avatar_filename)
                avatar_file.save(avatar_path)

        # ตรวจสอบการเปลี่ยนรหัสผ่าน
        new_password_hash = user['password_hash']
        if current_password or new_password or confirm_new_password:
            if not current_password:
                conn.close()
                flash('กรุณาระบุรหัสผ่านปัจจุบันเพื่อเปลี่ยนรหัสผ่านใหม่', 'danger')
                return render_template('profile.html', user=user)

            if not check_password_hash(user['password_hash'], current_password):
                conn.close()
                flash('รหัสผ่านปัจจุบันไม่ถูกต้อง', 'danger')
                return render_template('profile.html', user=user)

            is_valid_pw, pw_err_msg = validate_password_strength(new_password)
            if not is_valid_pw:
                conn.close()
                flash(pw_err_msg, 'danger')
                return render_template('profile.html', user=user)

            if new_password != confirm_new_password:
                conn.close()
                flash('รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน', 'danger')
                return render_template('profile.html', user=user)

            new_password_hash = generate_password_hash(new_password)

        # อัปเดตข้อมูลผู้ใช้
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET name = ?, email = ?, phone = ?, address = ?, avatar = ?, password_hash = ?
            WHERE id = ?
        """, (name, email, phone, address, avatar_filename, new_password_hash, session['user_id']))
        conn.commit()
        conn.close()

        # อัปเดตชื่อในเซสชัน
        session['user_name'] = name
        flash('อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว', 'success')
        return redirect(url_for('auth.profile'))

    conn.close()
    return render_template('profile.html', user=user)
