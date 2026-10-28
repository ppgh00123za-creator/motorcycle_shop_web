import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

links = []
forms = []

for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, TEMPLATES_DIR).replace('\\', '/')
            with open(filepath, 'r', encoding='utf-8') as fp:
                content = fp.read()
            for m in re.finditer(r'href=["\']([^"\']+)["\']', content):
                links.append((rel_path, m.group(1)))
            for m in re.finditer(r'action=["\']([^"\']+)["\']', content):
                forms.append((rel_path, m.group(1)))

print(f"Total links found: {len(links)}")
print(f"Total forms found: {len(forms)}")

# Find any links that are '#', empty, or javascript:void(0)
empty_links = [l for l in links if l[1] in ('#', '', 'javascript:void(0);', 'javascript:;')]
print(f"\nEmpty/hash links ({len(empty_links)}):")
for tmpl, target in empty_links:
    print(f"   {tmpl}: href='{target}'")
