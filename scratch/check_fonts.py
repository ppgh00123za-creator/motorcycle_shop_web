import os
import sys
from reportlab.pdfbase.ttfonts import TTFontFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

for font_path in [
    os.path.join(FONT_DIR, 'Sarabun-Regular.ttf'),
    os.path.join(FONT_DIR, 'Sarabun-Bold.ttf'),
    'C:\\Windows\\Fonts\\tahoma.ttf',
    'C:\\Windows\\Fonts\\tahomabd.ttf'
]:
    if os.path.exists(font_path):
        ttf = TTFontFile(font_path)
        # Check CMAP
        cmap = ttf.charToGlyph
        thai_chars = [c for c in cmap.keys() if 0x0E00 <= c <= 0x0E7F]
        pua_chars = [c for c in cmap.keys() if 0xF700 <= c <= 0xF71A or 0xF000 <= c <= 0xF0FF]
        print(f"Font: {os.path.basename(font_path)}")
        print(f"   Total glyphs: {len(cmap)}")
        print(f"   Thai chars (0E00-0E7F): {len(thai_chars)}")
        print(f"   Thai PUA chars: {len(pua_chars)} -> {[hex(c) for c in sorted(pua_chars)]}")
