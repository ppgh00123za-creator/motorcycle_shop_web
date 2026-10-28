import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, TEMPLATES_DIR).replace('\\', '/')
            with open(filepath, 'r', encoding='utf-8') as fp:
                content = fp.read()
            for macro_name in ['product_card', 'status_badge', 'payment_badge']:
                if re.search(r'\b' + macro_name + r'\s*\(', content):
                    # Check if imported
                    if f"import {macro_name}" not in content and f"import" not in content:
                        print(f"MISSING IMPORT: {rel_path} uses {macro_name}() but doesn't import it!")
                    elif macro_name not in re.findall(r"import\s+([^%}\n]+)", content)[0] if "import" in content else True:
                        # check specifically
                        imports = re.findall(r"import\s+([^\n%]+)", content)
                        all_imported = " ".join(imports)
                        if macro_name not in all_imported:
                            print(f"MISSING IMPORT: {rel_path} uses {macro_name}() but only imported: {imports}")
