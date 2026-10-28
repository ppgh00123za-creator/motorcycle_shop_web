import os
import re
import ast
import jinja2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
ROUTES_DIR = os.path.join(BASE_DIR, 'routes')

# Find all render_template calls in routes
pattern = re.compile(r"render_template\(\s*['\"]([^'\"]+)['\"]((?:[^)]|\n)*)\)", re.MULTILINE)

route_files = [os.path.join(ROUTES_DIR, f) for f in os.listdir(ROUTES_DIR) if f.endswith('.py')]
app_file = os.path.join(BASE_DIR, 'app.py')
all_py_files = route_files + [app_file]

print("Scanning render_template calls across Python files...\n")
renders = {}
for py_path in all_py_files:
    fname = os.path.basename(py_path)
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex search for render_template calls
    matches = re.finditer(r"render_template\(\s*['\"]([^'\"]+)['\"]([^)]*)\)", content, re.DOTALL)
    for m in matches:
        tmpl_name = m.group(1)
        args_str = m.group(2)
        # extract keyword args
        kwargs = set()
        for kw in re.finditer(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=", args_str):
            kwargs.add(kw.group(1))
        # Also check for simple variable passing if any (though usually kwargs)
        renders.setdefault(tmpl_name, []).append((fname, kwargs))

for tmpl, callers in sorted(renders.items()):
    print(f"Template: {tmpl}")
    for caller, kwargs in callers:
        print(f"   From {caller}: kwargs={sorted(kwargs)}")
