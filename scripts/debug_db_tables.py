import sqlite3
import os
from django.conf import settings

# 1. Check file existence
db_path = r"c:\dev\Forkast\db.sqlite3"
print(f"Checking DB at: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

# 2. Check Tables
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print("\n[Existing Tables]")
    for t in tables:
        if 'platform_ui' in t:
            print(f"- {t}")
    
    if 'platform_ui_order' in tables:
        print("\n✅ 'platform_ui_order' MATCH FOUND.")
    else:
        print("\n❌ 'platform_ui_order' MATCH NOT FOUND.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
