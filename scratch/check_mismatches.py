import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
import re
import jinja2
from jinja2 import meta
from app import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
ROUTES_DIR = os.path.join(BASE_DIR, 'routes')

env = app.jinja_env
context_globals = set(app.jinja_env.globals.keys())

# Map template path to undeclared variables
tmpl_undeclared = {}
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            rel_path = os.path.relpath(os.path.join(root, f), TEMPLATES_DIR).replace('\\', '/')
            with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                src = fp.read()
            try:
                ast_tree = env.parse(src)
                undeclared = meta.find_undeclared_variables(ast_tree)
                tmpl_undeclared[rel_path] = undeclared - context_globals - {'super', 'request', 'session', 'g'}
            except Exception as e:
                print(f"Error {rel_path}: {e}")

# Map template to kwargs passed by routes
py_files = [os.path.join(ROUTES_DIR, f) for f in os.listdir(ROUTES_DIR) if f.endswith('.py')] + [os.path.join(BASE_DIR, 'app.py')]
tmpl_calls = {}

for py_path in py_files:
    fname = os.path.basename(py_path)
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for m in re.finditer(r"render_template\(\s*['\"]([^'\"]+)['\"]([^)]*)\)", content, re.DOTALL):
        tmpl = m.group(1)
        args_str = m.group(2)
        kwargs = set(re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=", args_str))
        tmpl_calls.setdefault(tmpl, []).append((fname, kwargs))

print("=== Checking Variable Mismatches ===")
for tmpl, callers in sorted(tmpl_calls.items()):
    needed = tmpl_undeclared.get(tmpl, set())
    # macro imports or internal blocks
    for caller, kwargs in callers:
        missing = needed - kwargs
        # exclude macros that might be defined in the template or imported
        if missing:
            print(f"Template '{tmpl}' called from {caller}:")
            print(f"   Missing in kwargs: {sorted(missing)}")
            print(f"   Passed in kwargs:  {sorted(kwargs)}\n")
