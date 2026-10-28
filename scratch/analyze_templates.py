import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
import re
import jinja2
from jinja2 import meta

from app import app
env = app.jinja_env
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')

# Global variables in templates (from context processors or Jinja builtins)
# Let's inspect context processors in app.py
from app import app
context_globals = set(app.jinja_env.globals.keys())
print(f"Context globals: {sorted(context_globals)}\n")

for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            rel_path = os.path.relpath(os.path.join(root, f), TEMPLATES_DIR).replace('\\', '/')
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
                    src = fp.read()
                ast = env.parse(src)
                undeclared = jinja2.meta.find_undeclared_variables(ast)
                # Filter out context globals and loop vars
                unresolved = undeclared - context_globals - {'super', 'request', 'session', 'g'}
                print(f"Template: {rel_path}")
                print(f"   Undeclared vars: {sorted(unresolved)}")
            except Exception as e:
                print(f"Error parsing {rel_path}: {e}")
