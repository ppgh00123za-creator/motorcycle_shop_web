import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uharfbuzz

f = TTFont('SarabunTH', 'static/fonts/Sarabun-Regular.ttf')
pdfmetrics.registerFont(f)

for word in ["ที่", "นี้", "ผู้", "ซื้อ", "สิทธิ์", "ชำระเงินแล้ว", "160 ธีระ สายซิ่ง"]:
    buf = uharfbuzz.Buffer()
    buf.add_str(word)
    buf.guess_segment_properties()
    hb_font = f.hbFont(12)
    uharfbuzz.shape(hb_font, buf)
    infos = buf.glyph_infos
    positions = buf.glyph_positions
    print(f"\nWord: {word}")
    for info, pos in zip(infos, positions):
        print(f"  gid={info.codepoint}, cluster={info.cluster}, x_adv={pos.x_advance}, y_adv={pos.y_advance}, x_off={pos.x_offset}, y_off={pos.y_offset}")
