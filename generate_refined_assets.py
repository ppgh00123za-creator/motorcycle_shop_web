"""
generate_refined_assets.py
สร้างภาพกราฟิก SVG ของรถมอเตอร์ไซค์ทั้ง 20 รุ่นแบบแยกรายละเอียดรูปทรงเฉพาะตัว
(Underbone ครอบครัว, Automatic สกู๊ตเตอร์, Maxi-scooter, Sport Fairing, และ Mini-streetfighter)
พร้อมสร้างภาพ Placeholder สำรอง และบันทึกทั้งชื่อเต็มภาษาอังกฤษและชื่อเดิม
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

# 20 โมเดลพร้อมรายละเอียดรูปทรงและสีเฉพาะรุ่น
BIKE_MODELS = [
    # 1. Honda Wave 110i
    {
        'brand': 'Honda', 'model': 'Wave 110i', 'year': '2024', 'cc': 109, 'category': 'ครอบครัว',
        'type': 'underbone', 'color1': '#d90429', 'color2': '#1e1e24', 'accent': '#ef233c',
        'new_file': 'honda_wave_110i.svg', 'legacy_file': 'wave110i.svg', 'status': 'available'
    },
    # 2. Honda Wave 125i
    {
        'brand': 'Honda', 'model': 'Wave 125i', 'year': '2024', 'cc': 124, 'category': 'ครอบครัว',
        'type': 'underbone_premium', 'color1': '#8d0801', 'color2': '#bf0603', 'accent': '#d90429',
        'new_file': 'honda_wave_125i.svg', 'legacy_file': 'wave125i.svg', 'status': 'available'
    },
    # 3. Honda Dream 100
    {
        'brand': 'Honda', 'model': 'Dream 100 รุ่นเก่า', 'year': 'ไม่ทราบปี', 'cc': 97, 'category': 'ครอบครัว',
        'type': 'classic_cub', 'color1': '#2b2d42', 'color2': '#4a4e69', 'accent': '#8d99ae',
        'new_file': 'honda_dream_100.svg', 'legacy_file': 'dream100.svg', 'status': 'discontinued'
    },
    # 4. Honda Super Cub 110
    {
        'brand': 'Honda', 'model': 'Super Cub 110', 'year': '2024', 'cc': 109, 'category': 'ครอบครัว',
        'type': 'retro_cub', 'color1': '#d90429', 'color2': '#f4f1de', 'accent': '#e07a5f',
        'new_file': 'honda_super_cub_110.svg', 'legacy_file': 'supercub110.svg', 'status': 'available'
    },
    # 5. Yamaha Finn
    {
        'brand': 'Yamaha', 'model': 'Finn', 'year': '2024', 'cc': 114, 'category': 'ครอบครัว',
        'type': 'underbone', 'color1': '#003566', 'color2': '#0077b6', 'accent': '#00b4d8',
        'new_file': 'yamaha_finn.svg', 'legacy_file': 'finn.svg', 'status': 'available'
    },
    # 6. Honda Scoopy
    {
        'brand': 'Honda', 'model': 'Scoopy', 'year': '2024', 'cc': 109, 'category': 'ออโตเมติก',
        'type': 'fashion_scooter', 'color1': '#d90429', 'color2': '#f72585', 'accent': '#ffb703',
        'new_file': 'honda_scoopy.svg', 'legacy_file': 'scoopy.svg', 'status': 'available'
    },
    # 7. Honda Click 125i
    {
        'brand': 'Honda', 'model': 'Click 125i', 'year': '2024', 'cc': 124, 'category': 'ออโตเมติก',
        'type': 'sport_scooter', 'color1': '#d90429', 'color2': '#2b2d42', 'accent': '#ef233c',
        'new_file': 'honda_click_125i.svg', 'legacy_file': 'click125.svg', 'status': 'available'
    },
    # 8. Honda Click 150i
    {
        'brand': 'Honda', 'model': 'Click 150i', 'year': '2020', 'cc': 149, 'category': 'ออโตเมติก',
        'type': 'sport_scooter', 'color1': '#b80322', 'color2': '#141416', 'accent': '#e63946',
        'new_file': 'honda_click_150i.svg', 'legacy_file': 'click150.svg', 'status': 'available'
    },
    # 9. Honda Click 160
    {
        'brand': 'Honda', 'model': 'Click 160', 'year': '2024', 'cc': 156, 'category': 'ออโตเมติก',
        'type': 'sport_scooter_wide', 'color1': '#d90429', 'color2': '#111113', 'accent': '#ef233c',
        'new_file': 'honda_click_160.svg', 'legacy_file': 'click160.svg', 'status': 'available'
    },
    # 10. Honda PCX 150
    {
        'brand': 'Honda', 'model': 'PCX 150 รุ่นเก่า', 'year': '2019', 'cc': 149, 'category': 'ออโตเมติก',
        'type': 'maxi_scooter', 'color1': '#4a4e69', 'color2': '#222226', 'accent': '#9a8c98',
        'new_file': 'honda_pcx_150.svg', 'legacy_file': 'pcx150.svg', 'status': 'discontinued'
    },
    # 11. Honda PCX 160
    {
        'brand': 'Honda', 'model': 'PCX 160', 'year': '2024', 'cc': 156, 'category': 'ออโตเมติก',
        'type': 'maxi_scooter', 'color1': '#d90429', 'color2': '#1a1a24', 'accent': '#ef233c',
        'new_file': 'honda_pcx_160.svg', 'legacy_file': 'pcx160.svg', 'status': 'available'
    },
    # 12. Honda Lead 125
    {
        'brand': 'Honda', 'model': 'Lead 125', 'year': '2024', 'cc': 124, 'category': 'ออโตเมติก',
        'type': 'commuter_scooter', 'color1': '#2b2d42', 'color2': '#d90429', 'accent': '#8d99ae',
        'new_file': 'honda_lead_125.svg', 'legacy_file': 'lead125.svg', 'status': 'available'
    },
    # 13. Yamaha Fino 115
    {
        'brand': 'Yamaha', 'model': 'Fino 115 รุ่นเก่า', 'year': 'ไม่ทราบปี', 'cc': 113, 'category': 'ออโตเมติก',
        'type': 'fashion_scooter', 'color1': '#003566', 'color2': '#4a4e69', 'accent': '#0077b6',
        'new_file': 'yamaha_fino_115.svg', 'legacy_file': 'fino115.svg', 'status': 'discontinued'
    },
    # 14. Yamaha Grand Filano
    {
        'brand': 'Yamaha', 'model': 'Grand Filano', 'year': '2024', 'cc': 124, 'category': 'ออโตเมติก',
        'type': 'fashion_scooter', 'color1': '#003566', 'color2': '#f08080', 'accent': '#0077b6',
        'new_file': 'yamaha_grand_filano.svg', 'legacy_file': 'grandfilano.svg', 'status': 'available'
    },
    # 15. Yamaha Aerox 155
    {
        'brand': 'Yamaha', 'model': 'Aerox 155', 'year': '2024', 'cc': 155, 'category': 'ออโตเมติก',
        'type': 'sport_scooter_wide', 'color1': '#003566', 'color2': '#023e8a', 'accent': '#0096c7',
        'new_file': 'yamaha_aerox_155.svg', 'legacy_file': 'aerox155.svg', 'status': 'available'
    },
    # 16. Yamaha NMAX 155
    {
        'brand': 'Yamaha', 'model': 'NMAX 155', 'year': '2024', 'cc': 155, 'category': 'ออโตเมติก',
        'type': 'maxi_scooter', 'color1': '#001d3d', 'color2': '#003566', 'accent': '#0077b6',
        'new_file': 'yamaha_nmax_155.svg', 'legacy_file': 'nmax155.svg', 'status': 'available'
    },
    # 17. Honda MSX 125
    {
        'brand': 'Honda', 'model': 'MSX 125', 'year': '2021', 'cc': 124, 'category': 'สปอร์ต/มินิ',
        'type': 'mini_street', 'color1': '#d90429', 'color2': '#ffd166', 'accent': '#ef233c',
        'new_file': 'honda_msx_125.svg', 'legacy_file': 'msx125.svg', 'status': 'available'
    },
    # 18. Honda CBR150R
    {
        'brand': 'Honda', 'model': 'CBR150R', 'year': '2024', 'cc': 149, 'category': 'สปอร์ต/มินิ',
        'type': 'racing_sport', 'color1': '#d90429', 'color2': '#111113', 'accent': '#ef233c',
        'new_file': 'honda_cbr150r.svg', 'legacy_file': 'cbr150r.svg', 'status': 'available'
    },
    # 19. Yamaha R15
    {
        'brand': 'Yamaha', 'model': 'R15', 'year': '2024', 'cc': 155, 'category': 'สปอร์ต/มินิ',
        'type': 'racing_sport', 'color1': '#003566', 'color2': '#001233', 'accent': '#0077b6',
        'new_file': 'yamaha_r15.svg', 'legacy_file': 'r15.svg', 'status': 'available'
    },
    # 20. Suzuki Raider R150
    {
        'brand': 'Suzuki', 'model': 'Raider R150', 'year': '2023', 'cc': 147, 'category': 'สปอร์ต/มินิ',
        'type': 'hyper_underbone', 'color1': '#1d3557', 'color2': '#457b9d', 'accent': '#e63946',
        'new_file': 'suzuki_raider_r150.svg', 'legacy_file': 'raider150.svg', 'status': 'available'
    }
]

def render_svg(b):
    brand = b['brand']
    model = b['model']
    year = b.get('year', '')
    cc = b['cc']
    cat = b['category']
    c1 = b['color1']
    c2 = b['color2']
    accent = b['accent']
    b_type = b['type']
    status = b['status']

    status_tag = ''
    if status == 'discontinued':
        status_tag = '<rect x="420" y="20" width="160" height="34" rx="17" fill="#6c757d"/><text x="500" y="42" font-family="sans-serif" font-size="14" fill="#ffffff" text-anchor="middle" font-weight="bold">รุ่นเลิกจำหน่าย</text>'

    # สไตล์โครงรถที่แตกต่างตามประเภทยานพาหนะ
    if b_type == 'underbone' or b_type == 'underbone_premium':
        # รถครอบครัว ทรงเพรียวลม ล้อ 17 นิ้ว
        chassis_svg = f'''
        <!-- Wheels -->
        <circle cx="85" cy="180" r="54" fill="none" stroke="#252528" stroke-width="14"/>
        <circle cx="85" cy="180" r="46" fill="none" stroke="{accent}" stroke-width="3" opacity="0.5"/>
        <circle cx="85" cy="180" r="20" fill="#141416" stroke="#444" stroke-width="4"/>
        <circle cx="365" cy="180" r="54" fill="none" stroke="#252528" stroke-width="14"/>
        <circle cx="365" cy="180" r="46" fill="none" stroke="{accent}" stroke-width="3" opacity="0.5"/>
        <circle cx="365" cy="180" r="20" fill="#141416" stroke="#444" stroke-width="4"/>
        <!-- Frame & Fairing -->
        <path d="M 85 180 L 180 150 L 250 115 L 330 85 L 365 180" fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
        <!-- Curved Step-through Cover -->
        <path d="M 175 140 C 210 110, 270 100, 315 110 L 330 145 L 240 155 Z" fill="{c1}" opacity="0.95"/>
        <path d="M 140 120 C 180 115, 220 118, 250 130 L 245 145 L 145 135 Z" fill="#18181c" stroke="#444" stroke-width="2"/>
        <!-- Front Shield -->
        <path d="M 290 85 L 345 130 L 320 165 Z" fill="{c2}" opacity="0.9"/>
        <line x1="320" y1="85" x2="335" y2="58" stroke="#777" stroke-width="8" stroke-linecap="round"/>
        <circle cx="342" cy="62" r="9" fill="#f8f9fa"/>
        <!-- Exhaust -->
        <path d="M 200 165 L 140 180 L 65 185" fill="none" stroke="#888" stroke-width="8" stroke-linecap="round"/>
        '''
    elif b_type in ['classic_cub', 'retro_cub']:
        # รถเรโทร คลาสสิก บังลมโค้งมน
        chassis_svg = f'''
        <!-- Wheels -->
        <circle cx="85" cy="180" r="54" fill="none" stroke="#2b2d42" stroke-width="12"/>
        <circle cx="85" cy="180" r="46" fill="none" stroke="#fff" stroke-width="2" opacity="0.4"/>
        <circle cx="85" cy="180" r="18" fill="#141416" stroke="#888" stroke-width="4"/>
        <circle cx="365" cy="180" r="54" fill="none" stroke="#2b2d42" stroke-width="12"/>
        <circle cx="365" cy="180" r="46" fill="none" stroke="#fff" stroke-width="2" opacity="0.4"/>
        <circle cx="365" cy="180" r="18" fill="#141416" stroke="#888" stroke-width="4"/>
        <!-- Retro Curved Leg Shield -->
        <path d="M 250 100 C 290 85, 340 100, 345 150 L 310 165 C 290 130, 260 120, 240 125 Z" fill="{c2}" opacity="0.95"/>
        <path d="M 145 125 C 185 110, 230 115, 255 125 L 250 145 L 150 140 Z" fill="{c1}"/>
        <!-- Round Headlight -->
        <circle cx="340" cy="65" r="14" fill="#ffffff" stroke="{c1}" stroke-width="4"/>
        <circle cx="340" cy="65" r="7" fill="#ffeaa7"/>
        <line x1="315" y1="90" x2="335" y2="70" stroke="#666" stroke-width="7" stroke-linecap="round"/>
        <!-- Straight Exhaust -->
        <path d="M 200 168 L 130 182 L 65 185" fill="none" stroke="#aaa" stroke-width="7" stroke-linecap="round"/>
        '''
    elif b_type == 'maxi_scooter':
        # บิ๊กสกู๊ตเตอร์/แม็กซี่ ทรงใหญ่ พรีเมียม บังลมหน้าสูง
        chassis_svg = f'''
        <!-- Wheels (smaller diameter, wider tire) -->
        <circle cx="85" cy="185" r="48" fill="none" stroke="#222" stroke-width="20"/>
        <circle cx="85" cy="185" r="38" fill="none" stroke="{accent}" stroke-width="4" opacity="0.7"/>
        <circle cx="85" cy="185" r="18" fill="#141416" stroke="#555" stroke-width="5"/>
        <circle cx="365" cy="185" r="48" fill="none" stroke="#222" stroke-width="20"/>
        <circle cx="365" cy="185" r="38" fill="none" stroke="{accent}" stroke-width="4" opacity="0.7"/>
        <circle cx="365" cy="185" r="18" fill="#141416" stroke="#555" stroke-width="5"/>
        <!-- Full Fairing Body (Large PCX/NMAX Maxi silhouette) -->
        <path d="M 85 185 L 145 145 L 210 135 L 285 140 L 345 105 L 375 145 L 365 185" fill="{c2}" opacity="0.95"/>
        <!-- Windscreen (ชิวหน้าทรงสูง) -->
        <polygon points="325,100 345,55 365,65 350,110" fill="rgba(255,255,255,0.45)" stroke="#888" stroke-width="1.5"/>
        <!-- Main Red/Brand Accent Stripe -->
        <path d="M 160 145 C 220 115, 290 115, 340 120 L 330 145 L 210 150 Z" fill="{c1}"/>
        <!-- Stepped Plush Seat (เบาะนั่งสองตอน) -->
        <path d="M 130 135 C 160 120, 210 120, 240 135 L 235 150 L 135 145 Z" fill="#111" stroke="#444" stroke-width="2"/>
        <!-- Headlight cluster -->
        <polygon points="350,120 375,125 360,140" fill="#fff"/>
        <!-- Big Exhaust Box -->
        <rect x="75" y="165" width="110" height="22" rx="10" fill="#333" stroke="#555" stroke-width="2"/>
        '''
    elif b_type in ['sport_scooter', 'sport_scooter_wide']:
        # สปอร์ตเอที (Click / Aerox) เหลี่ยมคม โฉบเฉี่ยว
        chassis_svg = f'''
        <!-- Wheels -->
        <circle cx="85" cy="182" r="50" fill="none" stroke="#222" stroke-width="16"/>
        <circle cx="85" cy="182" r="40" fill="none" stroke="{accent}" stroke-width="3" opacity="0.6"/>
        <circle cx="85" cy="182" r="18" fill="#111" stroke="#555" stroke-width="4"/>
        <circle cx="365" cy="182" r="50" fill="none" stroke="#222" stroke-width="16"/>
        <circle cx="365" cy="182" r="40" fill="none" stroke="{accent}" stroke-width="3" opacity="0.6"/>
        <circle cx="365" cy="182" r="18" fill="#111" stroke="#555" stroke-width="4"/>
        <!-- Angular Sharp Body (Click / Aerox V-Shape) -->
        <polygon points="120,150 200,125 280,125 350,95 375,130 330,165 240,165 170,160" fill="{c2}"/>
        <polygon points="190,125 270,125 340,105 320,135 220,145" fill="{c1}"/>
        <!-- Sharp V-Headlight -->
        <polygon points="345,100 375,115 355,130" fill="#ffffff"/>
        <!-- Sharp Seat -->
        <path d="M 130 130 C 165 120, 205 120, 240 130 L 235 145 L 135 140 Z" fill="#1a1a1c" stroke="#444" stroke-width="2"/>
        <!-- Upswept Exhaust -->
        <polygon points="75,175 160,155 165,170 85,185" fill="#444" stroke="#666" stroke-width="1"/>
        '''
    elif b_type == 'racing_sport':
        # เรซซิ่งสปอร์ต ฟูลแฟริ่ง (CBR150R / R15)
        chassis_svg = f'''
        <!-- Wheels with Wide Rim -->
        <circle cx="85" cy="180" r="52" fill="none" stroke="#1f2024" stroke-width="16"/>
        <circle cx="85" cy="180" r="42" fill="none" stroke="{accent}" stroke-width="4" opacity="0.8"/>
        <circle cx="85" cy="180" r="20" fill="#111" stroke="#666" stroke-width="4"/>
        <circle cx="365" cy="180" r="52" fill="none" stroke="#1f2024" stroke-width="16"/>
        <circle cx="365" cy="180" r="42" fill="none" stroke="{accent}" stroke-width="4" opacity="0.8"/>
        <circle cx="365" cy="180" r="20" fill="#111" stroke="#666" stroke-width="4"/>
        <!-- Racing Deltabox Frame & Full Fairing -->
        <polygon points="100,140 180,130 250,90 320,80 375,115 340,170 230,170 160,165" fill="{c1}"/>
        <!-- Lower Fairing Belly Pan -->
        <polygon points="180,165 310,165 330,150 200,150" fill="{c2}"/>
        <!-- Windscreen & Clip-on Handlebars -->
        <polygon points="310,80 340,45 365,58 340,95" fill="rgba(255,255,255,0.4)" stroke="#aaa" stroke-width="1.5"/>
        <line x1="320" y1="85" x2="335" y2="65" stroke="#ccc" stroke-width="6"/>
        <!-- Split Headlight -->
        <polygon points="345,95 375,110 360,118" fill="#ffffff"/>
        <!-- Racing Upward Seat Tail -->
        <polygon points="90,140 150,130 190,135 150,150" fill="#111" stroke="#444" stroke-width="1.5"/>
        <!-- Sport Exhaust -->
        <polygon points="90,170 170,150 175,165 100,182" fill="#555" stroke="#777" stroke-width="1.5"/>
        '''
    else:
        # มินิไบค์ หรือ สตรีทไบค์ (MSX 125 / Raider / อื่นๆ)
        chassis_svg = f'''
        <!-- Wheels -->
        <circle cx="95" cy="185" r="46" fill="none" stroke="#222" stroke-width="18"/>
        <circle cx="95" cy="185" r="36" fill="none" stroke="{accent}" stroke-width="3" opacity="0.6"/>
        <circle cx="95" cy="185" r="16" fill="#111" stroke="#555" stroke-width="4"/>
        <circle cx="355" cy="185" r="46" fill="none" stroke="#222" stroke-width="18"/>
        <circle cx="355" cy="185" r="36" fill="none" stroke="{accent}" stroke-width="3" opacity="0.6"/>
        <circle cx="355" cy="185" r="16" fill="#111" stroke="#555" stroke-width="4"/>
        <!-- Exposed Frame / Trellis Lines -->
        <path d="M 95 185 L 180 145 L 245 90 L 320 80 L 355 185" fill="none" stroke="#555" stroke-width="9" stroke-linecap="round"/>
        <!-- Upside Down Gold Fork (โช้กทอง) -->
        <line x1="310" y1="80" x2="355" y2="185" stroke="#ffd166" stroke-width="7" stroke-linecap="round"/>
        <!-- Compact Tank & Fairing -->
        <path d="M 180 120 C 215 75, 265 75, 295 90 L 305 125 L 225 140 Z" fill="{c1}"/>
        <!-- Street Seat -->
        <path d="M 135 120 C 170 110, 205 110, 230 120 L 225 135 L 140 130 Z" fill="#1a1a1c" stroke="#444" stroke-width="2"/>
        <circle cx="330" cy="65" r="9" fill="#fff"/>
        <path d="M 185 160 L 130 175 L 75 180" fill="none" stroke="#777" stroke-width="7" stroke-linecap="round"/>
        '''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#141416" />
      <stop offset="100%" stop-color="#1f2026" />
    </linearGradient>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{c1}" />
      <stop offset="100%" stop-color="{accent}" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="8" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="600" height="400" rx="16" fill="url(#bgGrad)"/>
  <circle cx="500" cy="110" r="160" fill="{c1}" opacity="0.08"/>
  <circle cx="100" cy="300" r="130" fill="{accent}" opacity="0.05"/>

  <!-- Top Brand Tag -->
  <path d="M 0 0 L 220 0 L 180 54 L 0 54 Z" fill="url(#brandGrad)" />
  <text x="32" y="35" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="22" font-weight="900" fill="#ffffff" letter-spacing="1.5">{brand.upper()}</text>

  <!-- Status badge -->
  {status_tag}

  <!-- Motorcycle Chassis Graphic -->
  <g transform="translate(75, 80)" filter="url(#shadow)">
    {chassis_svg}
  </g>

  <!-- Bottom Info Container -->
  <rect x="24" y="300" width="552" height="76" rx="12" fill="rgba(255, 255, 255, 0.04)" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>

  <!-- Model Title & Specs -->
  <text x="44" y="333" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="20" font-weight="700" fill="#ffffff">{model}</text>
  <text x="44" y="357" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="13" fill="#9999a5">ประเภท: {cat} | พิกัด ≤ 160 cc ({year})</text>

  <!-- CC Badge -->
  <rect x="456" y="316" width="100" height="42" rx="8" fill="{c1}"/>
  <text x="506" y="343" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="17" font-weight="800" fill="#ffffff" text-anchor="middle">{cc} cc</text>
</svg>'''
    return svg


def render_placeholder():
    """สร้างภาพสำรองเมื่อโหลดรูปหลักไม่สำเร็จ (Fallback Placeholder)"""
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="pGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1e24" />
      <stop offset="100%" stop-color="#2b2d42" />
    </linearGradient>
  </defs>
  <rect width="600" height="400" rx="16" fill="url(#pGrad)"/>
  
  <!-- Dashed border -->
  <rect x="20" y="20" width="560" height="360" rx="12" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" stroke-dasharray="8 6"/>

  <!-- Motorcycle outline icon -->
  <g transform="translate(180, 110)" stroke="#8d99ae" stroke-width="5" fill="none">
    <circle cx="40" cy="110" r="35"/>
    <circle cx="200" cy="110" r="35"/>
    <path d="M 40 110 L 95 90 L 140 55 L 185 50 L 200 110" stroke-linecap="round"/>
    <path d="M 95 90 L 150 90 L 190 60"/>
    <line x1="180" y1="50" x2="190" y2="35" stroke-linecap="round"/>
  </g>

  <rect x="210" y="240" width="180" height="34" rx="17" fill="#d90429"/>
  <text x="300" y="262" font-family="'Prompt', sans-serif" font-size="14" font-weight="700" fill="#ffffff" text-anchor="middle">ภาพตัวอย่างสินค้า</text>
  <text x="300" y="305" font-family="'Prompt', sans-serif" font-size="15" fill="#8d99ae" text-anchor="middle">MOTO 160 BIKE SHOP • รูปสำรองทางการ</text>
</svg>'''


# บันทึกภาพทั้ง 20 รุ่น (ทั้งชื่อใหม่ที่อ่านง่าย และชื่อเดิม)
for b in BIKE_MODELS:
    svg_data = render_svg(b)
    # บันทึกไฟล์ชื่อใหม่ที่ชัดเจน เช่น honda_wave_110i.svg
    path_new = os.path.join(IMG_DIR, b['new_file'])
    with open(path_new, 'w', encoding='utf-8') as f:
        f.write(svg_data)
    # บันทึกไฟล์ชื่อเดิมเพื่อความเข้ากันได้แบบ 100% เช่น wave110i.svg
    path_legacy = os.path.join(IMG_DIR, b['legacy_file'])
    with open(path_legacy, 'w', encoding='utf-8') as f:
        f.write(svg_data)

# บันทึกไฟล์ placeholder สำรอง
with open(os.path.join(IMG_DIR, 'placeholder_bike.svg'), 'w', encoding='utf-8') as f:
    f.write(render_placeholder())

print("สร้างภาพ SVG คุณภาพสูง 20 รุ่น (เฉพาะรูปทรงแต่ละรุ่น) พร้อม Placeholder สำรองสำเร็จเรียบร้อย!")
