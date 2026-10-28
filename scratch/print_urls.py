import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import app

print("Registered URL Rules:")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    print(f"{rule.rule:<35} methods={sorted(rule.methods)} -> endpoint={rule.endpoint}")
