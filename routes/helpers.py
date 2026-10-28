"""
utils/helpers.py
ฟังก์ชันช่วยเหลือส่วนกลาง (Shared Helper Functions) สำหรับทั้งระบบ
ช่วยลดการเขียนโค้ดซ้ำ (DRY - Don't Repeat Yourself)
"""

DEFAULT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

def allowed_file(filename, allowed_extensions=None):
    """ตรวจสอบนามสกุลไฟล์ที่อนุญาตให้อัปโหลด"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS
    return ext in allowed
