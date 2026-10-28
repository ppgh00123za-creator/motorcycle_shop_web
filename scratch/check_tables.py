import os
from reportlab.pdfbase.ttfonts import TTFontFile

for path in ['static/fonts/Sarabun-Regular.ttf', 'C:\\Windows\\Fonts\\tahoma.ttf']:
    f = TTFontFile(path)
    print(path, "Tables:", list(f.seekTable.keys()) if hasattr(f, 'seekTable') else 'unknown')
