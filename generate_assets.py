"""
generate_assets.py
สคริปต์สร้างไฟล์ภาพ SVG Vector คุณภาพสูงสำหรับรถมอเตอร์ไซค์ทั้ง 20 รุ่น โลโก้ และแบนเนอร์ร้าน
"""

import os
import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

# ดึงข้อมูลจากฐานข้อมูล
DB_PATH = os.path.join(BASE_DIR, 'instance', 'motorcycle_shop.db')
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
products = conn.execute("SELECT code, brand, model, engine_cc, category, image_url, status FROM products").fetchall()
conn.close()

# การกำหนดสีของแต่ละแบรนด์
brand_colors = {
    'Honda': {'primary': '#d90429', 'accent': '#ef233c', 'light': '#fff0f3'},
    'Yamaha': {'primary': '#003566', 'accent': '#0077b6', 'light': '#edf6f9'},
    'Suzuki': {'primary': '#1d3557', 'accent': '#457b9d', 'light': '#f1faee'}
}

# 1. สร้างภาพ SVG สำหรับรถแต่ละรุ่น
for p in products:
    brand = p['brand']
    model = p['model']
    cc = p['engine_cc']
    category = p['category']
    filename = p['image_url']
    status = p['status']
    colors = brand_colors.get(brand, {'primary': '#333333', 'accent': '#666666', 'light': '#f8f9fa'})

    status_badge = ''
    if status == 'discontinued':
        status_badge = '<rect x="420" y="20" width="160" height="34" rx="17" fill="#6c757d"/><text x="500" y="42" font-family="sans-serif" font-size="14" fill="#ffffff" text-anchor="middle" font-weight="bold">รุ่นเลิกจำหน่าย</text>'
    elif status == 'out_of_stock':
        status_badge = '<rect x="420" y="20" width="160" height="34" rx="17" fill="#e63946"/><text x="500" y="42" font-family="sans-serif" font-size="14" fill="#ffffff" text-anchor="middle" font-weight="bold">สินค้าหมดชั่วคราว</text>'

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#141416" />
      <stop offset="100%" stop-color="#1f2024" />
    </linearGradient>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{colors['primary']}" />
      <stop offset="100%" stop-color="{colors['accent']}" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="600" height="400" rx="16" fill="url(#bgGrad)"/>
  <circle cx="500" cy="120" r="160" fill="{colors['primary']}" opacity="0.08"/>
  <circle cx="100" cy="300" r="130" fill="{colors['accent']}" opacity="0.05"/>

  <!-- Top Brand Tag -->
  <path d="M 0 0 L 220 0 L 180 56 L 0 56 Z" fill="url(#brandGrad)" />
  <text x="32" y="36" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="22" font-weight="900" fill="#ffffff" letter-spacing="1.5">{brand.upper()}</text>

  <!-- Status badge -->
  {status_badge}

  <!-- Motorcycle Vector Silhouette -->
  <g transform="translate(80, 85)" filter="url(#shadow)">
    <!-- Rear Wheel -->
    <circle cx="80" cy="170" r="54" fill="none" stroke="#333338" stroke-width="18"/>
    <circle cx="80" cy="170" r="44" fill="none" stroke="{colors['accent']}" stroke-width="4" opacity="0.5"/>
    <circle cx="80" cy="170" r="22" fill="#1e1e24" stroke="#555560" stroke-width="5"/>
    
    <!-- Front Wheel -->
    <circle cx="360" cy="170" r="54" fill="none" stroke="#333338" stroke-width="18"/>
    <circle cx="360" cy="170" r="44" fill="none" stroke="{colors['accent']}" stroke-width="4" opacity="0.5"/>
    <circle cx="360" cy="170" r="22" fill="#1e1e24" stroke="#555560" stroke-width="5"/>

    <!-- Frame Lines -->
    <path d="M 80 170 L 175 145 L 245 95 L 325 80 L 360 170" fill="none" stroke="#50505a" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M 175 145 L 265 145 L 340 100" fill="none" stroke="#2c2c34" stroke-width="9" stroke-linecap="round"/>
    
    <!-- Body Fairing / Tank -->
    <path d="M 155 120 C 190 70, 255 65, 295 85 L 320 115 L 240 140 Z" fill="url(#brandGrad)" opacity="0.95"/>
    
    <!-- Seat -->
    <path d="M 140 115 C 170 110, 205 110, 235 118 L 230 130 L 148 125 Z" fill="#1a1a1c" stroke="#44444c" stroke-width="2"/>

    <!-- Handlebars and Front Light -->
    <line x1="310" y1="85" x2="330" y2="58" stroke="#888894" stroke-width="8" stroke-linecap="round"/>
    <circle cx="340" cy="62" r="10" fill="#f8f9fa"/>
    <polygon points="340,56 390,45 390,78" fill="#ffffff" opacity="0.12"/>

    <!-- Exhaust -->
    <path d="M 195 160 L 140 175 L 60 180" fill="none" stroke="#777785" stroke-width="8" stroke-linecap="round"/>
  </g>

  <!-- Bottom Info Bar -->
  <rect x="24" y="300" width="552" height="76" rx="12" fill="rgba(255, 255, 255, 0.04)" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>

  <!-- Model & Category -->
  <text x="44" y="333" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="20" font-weight="700" fill="#ffffff">{model}</text>
  <text x="44" y="357" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="13" fill="#9999a5">ประเภท: {category} | พิกัดไม่เกิน 160 cc</text>

  <!-- CC Badge -->
  <rect x="456" y="316" width="100" height="42" rx="8" fill="{colors['primary']}"/>
  <text x="506" y="343" font-family="'Prompt', 'Segoe UI', sans-serif" font-size="17" font-weight="800" fill="#ffffff" text-anchor="middle">{cc} cc</text>
</svg>'''

    filepath = os.path.join(IMG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)

# 2. สร้าง Hero Banner สำหรับหน้าแรก (Modern Thai Honda style)
hero_banner_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 480" width="100%" height="100%">
  <defs>
    <linearGradient id="heroBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0a0c" />
      <stop offset="50%" stop-color="#141418" />
      <stop offset="100%" stop-color="#1d0a0e" />
    </linearGradient>
    <linearGradient id="redAccent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d90429" />
      <stop offset="100%" stop-color="#ef233c" />
    </linearGradient>
  </defs>

  <rect width="1400" height="480" fill="url(#heroBg)"/>
  
  <!-- Red decorative angular stripes -->
  <polygon points="900,0 1020,0 760,480 640,480" fill="url(#redAccent)" opacity="0.2"/>
  <polygon points="1050,0 1200,0 920,480 770,480" fill="url(#redAccent)" opacity="0.4"/>
  <polygon points="1230,0 1400,0 1100,480 930,480" fill="url(#redAccent)" opacity="0.8"/>
  
  <!-- Glow circle -->
  <circle cx="1150" cy="240" r="220" fill="#d90429" opacity="0.15"/>

  <!-- Motorcycle Silhouette Outline in Banner -->
  <g transform="translate(850, 100)" opacity="0.9">
    <circle cx="100" cy="220" r="70" fill="none" stroke="#ffffff" stroke-width="12" opacity="0.3"/>
    <circle cx="420" cy="220" r="70" fill="none" stroke="#ffffff" stroke-width="12" opacity="0.3"/>
    <path d="M 100 220 L 220 180 L 300 110 L 400 90 L 420 220" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.5"/>
    <path d="M 200 150 C 240 80, 320 80, 360 110 L 400 140 L 290 170 Z" fill="url(#redAccent)" opacity="0.8"/>
  </g>

  <!-- Typography -->
  <rect x="100" y="90" width="220" height="36" rx="6" fill="url(#redAccent)"/>
  <text x="115" y="114" font-family="'Prompt', sans-serif" font-size="14" font-weight="700" fill="#ffffff" letter-spacing="2">ศูนย์รวมรถจักรยานยนต์</text>
  
  <text x="100" y="185" font-family="'Prompt', sans-serif" font-size="52" font-weight="900" fill="#ffffff">
    MOTO SPORT 160 SHOP
  </text>
  <text x="100" y="240" font-family="'Prompt', sans-serif" font-size="28" font-weight="600" fill="#ef233c">
    มาตรฐานความแรง พิกัดเครื่องยนต์ไม่เกิน 160 ซีซี
  </text>
  <text x="100" y="285" font-family="'Prompt', sans-serif" font-size="17" fill="#cccccc">
    พร้อมส่งมอบรถครอบครัว ออโตเมติก และสปอร์ตไบค์ชั้นนำ รับประกันคุณภาพ พร้อมบริการหลังการขาย
  </text>

  <!-- Feature Pills -->
  <g transform="translate(100, 340)">
    <rect x="0" y="0" width="160" height="42" rx="21" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
    <text x="80" y="26" font-family="'Prompt', sans-serif" font-size="14" fill="#ffffff" text-anchor="middle">✓ รถแท้ 100%</text>

    <rect x="180" y="0" width="180" height="42" rx="21" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
    <text x="270" y="26" font-family="'Prompt', sans-serif" font-size="14" fill="#ffffff" text-anchor="middle">✓ ตรวจเช็กพร้อมขับ</text>

    <rect x="380" y="0" width="170" height="42" rx="21" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
    <text x="465" y="26" font-family="'Prompt', sans-serif" font-size="14" fill="#ffffff" text-anchor="middle">✓ ออกใบเสร็จทันที</text>
  </g>
</svg>'''

with open(os.path.join(IMG_DIR, 'hero_banner.svg'), 'w', encoding='utf-8') as f:
    f.write(hero_banner_svg)

# 3. Logo SVG
logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 60" width="100%" height="100%">
  <defs>
    <linearGradient id="logoRed" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d90429" />
      <stop offset="100%" stop-color="#ef233c" />
    </linearGradient>
  </defs>
  <!-- Wing Graphic inspired by motorcycle wings -->
  <path d="M 10 45 L 35 15 L 55 15 L 35 45 Z" fill="url(#logoRed)"/>
  <path d="M 28 45 L 50 15 L 70 15 L 48 45 Z" fill="url(#logoRed)" opacity="0.7"/>
  <circle cx="28" cy="20" r="5" fill="#ffffff"/>

  <!-- Logo Text -->
  <text x="80" y="32" font-family="'Prompt', sans-serif" font-size="22" font-weight="900" fill="#111111">MOTO<tspan fill="#d90429">160</tspan></text>
  <text x="80" y="47" font-family="'Prompt', sans-serif" font-size="10" font-weight="700" fill="#666666" letter-spacing="2">BIKE SHOP</text>
</svg>'''

with open(os.path.join(IMG_DIR, 'logo.svg'), 'w', encoding='utf-8') as f:
    f.write(logo_svg)

print("สร้าง Assets SVG (รูปภาพรถ 20 รุ่น, แบนเนอร์, โลโก้) สำเร็จเรียบร้อย!")
