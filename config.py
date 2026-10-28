"""
config.py
การกำหนดค่าหลักของร้าน "160 ธีระ สายซิ่ง" (160 Teera Sai Sing)
ศูนย์รวมข้อมูลร้าน การตั้งค่าระบบ และตำแหน่งไฟล์รูปภาพส่วนกลาง
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ข้อมูลตัวตนร้านค้า (Shop Identity)
SHOP_CONFIG = {
    'name': '160 ธีระ สายซิ่ง',
    'name_en': '160 Teera Sai Sing',
    'type': 'จำหน่ายรถมอเตอร์ไซค์ขนาดไม่เกิน 160 cc',
    'business_type': 'ศูนย์จำหน่ายรถจักรยานยนต์มาตรฐาน',
    'address': '899/22 หมู่บ้านศรีมงคล ต.ศิลา อ.เมืองขอนแก่น จ.ขอนแก่น 40000',
    'phone': '065-718-2338',
    'facebook': 'Teera Jantharasorn',
    'email': 'contact@160teerasaising.com',
    'tax_id': os.getenv('SHOP_TAX_ID', ''),  # เลขประจำตัวผู้เสียภาษี (ยังไม่ระบุ/รอจดทะเบียน)
    'vat_rate': 0.07,  # อัตราภาษีมูลค่าเพิ่ม 7% (คำนวณตอนสั่งซื้อเท่านั้น)
    'vat_percent': 7,
    'default_delivery_fee': 1500.0,  # ค่าจัดส่งมาตรฐานกรณีขนส่งระยะไกล
    'opening_days': 'วันพุธ',
    'opening_hours': '09:00 - 18:00 น.',
    'schedule_note': 'เปิดทำการทุกวันพุธ เวลา 09:00–18:00 น. (วันอื่นปิดทำการ)',
    'slogan': 'รถคู่ใจ สไตล์ที่ใช่ ในแบบของคุณ',
    'max_cc_limit': 160,
    # เส้นทางรูปภาพสำหรับเรียกผ่านเว็บ (URL Paths)
    'logo_url': '/รูปภาพ/โลโก้/840713524_1832489264431642_7798722595187389444_n (1).jpg',
    'banner_home_url': '/รูปภาพ/แบนเนอร์/842969582_1834627697533015_4502792330071360897_n.jpg',
    'banner_admin_url': '/รูปภาพ/แบนเนอร์/847415223_1288806816692961_3798483365911316880_n.jpg',
    'banner_dashboard_url': '/รูปภาพ/แบนเนอร์/848563004_4491144924470912_8231085618060152499_n.jpg',
    'banner_sidebar_url': '/รูปภาพ/แบนเนอร์/600 × 800 px.jpg',
    'background_url': '/รูปภาพ/พื้นหลัง/41bb23c5-02f9-42f0-beef-c6587186495e.png',
    'placeholder_bike_url': '/static/images/placeholder_bike.svg'
}

# ภาษีและค่าจัดส่ง
VAT_RATE = 0.07
DEFAULT_DELIVERY_FEE = 1500.0

# การกำหนดค่าระบบส่งอีเมล (SMTP Email Configuration)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() in ('true', '1', 'yes')
MAIL_FROM = os.getenv('MAIL_FROM', 'noreply@160teerasaising.com')

# แมปชื่อรุ่นรถเข้ากับไฟล์รูปภาพต้นฉบับในโฟลเดอร์ รูปภาพ/รถมอเตอร์ไซค์
PRODUCT_IMAGE_MAP = {
    'Wave 110i': 'รถมอเตอร์ไซค์/Honda Wave 110i — ความจุ 109 cc (ปี 2024).png',
    'Wave 125i': 'รถมอเตอร์ไซค์/Honda Wave 125i — ความจุ 124 cc (ปี 2024).webp',
    'Dream 100 รุ่นเก่า': 'รถมอเตอร์ไซค์/Honda Dream 100 รุ่นเก่า — ความจุ 97 cc.jpg',
    'Super Cub 110': 'รถมอเตอร์ไซค์/Honda Super Cub 110 — ความจุ 109 cc (ปี 2024).webp',
    'Finn': 'รถมอเตอร์ไซค์/Yamaha Finn — ความจุ 114 cc (ปี 2024).png',
    'Scoopy': 'รถมอเตอร์ไซค์/Honda Scoopy — ความจุ 109 cc (ปี 2024).jpg',
    'Click 125i': 'รถมอเตอร์ไซค์/Honda Click 125i — ความจุ 124 cc (ปี 2024).png',
    'Click 150i': 'รถมอเตอร์ไซค์/Honda Click 150i — ความจุ 149 cc (ปี 2020).jpg',
    'Click 160': 'รถมอเตอร์ไซค์/Honda Click 160 — ความจุ 156 cc (ปี 2024).png',
    'PCX 150 รุ่นเก่า': 'รถมอเตอร์ไซค์/Honda PCX 150 รุ่นเก่า — ความจุ 149 cc (ปี 2019).jpg',
    'PCX 160': 'รถมอเตอร์ไซค์/Honda PCX 160 — ความจุ 156 cc (ปี 2024).webp',
    'Lead 125': 'รถมอเตอร์ไซค์/Honda Lead 125 — ความจุ 124 cc (ปี 2024).png',
    'Fino 115 รุ่นเก่า': 'รถมอเตอร์ไซค์/Yamaha Fino 115 รุ่นเก่า — ความจุ 113 cc (ไม่ทราบปี).png',
    'Grand Filano': 'รถมอเตอร์ไซค์/Yamaha Grand Filano — ความจุ 124 cc (ปี 2024).png',
    'Aerox 155': 'รถมอเตอร์ไซค์/Yamaha Aerox 155 — ความจุ 155 cc (ปี 2024).png',
    'NMAX 155': 'รถมอเตอร์ไซค์/Yamaha NMAX 155 — ความจุ 155 cc (ปี 2024).webp',
    'MSX 125': 'รถมอเตอร์ไซค์/Honda MSX 125 — ความจุ 124 cc (ปี 2021).png',
    'CBR150R': 'รถมอเตอร์ไซค์/Honda CBR150R — ความจุ 149 cc (ปี 2024).png',
    'R15': 'รถมอเตอร์ไซค์/Yamaha R15 — ความจุ 155 cc (ปี 2024).png',
    'Raider R150': 'รถมอเตอร์ไซค์/Suzuki Raider R150 — ความจุ 147 cc (ปี 2023).jpg',
}
