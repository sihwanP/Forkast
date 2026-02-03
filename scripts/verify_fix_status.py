import sqlite3
import os
import datetime
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

DB_PATH = settings.DATABASES['default']['NAME']
print(f"--- VERIFICATION REPORT ---")
print(f"Django DB Path: {DB_PATH}")

if os.path.exists(DB_PATH):
    stat = os.stat(DB_PATH)
    print(f"DB File Size: {stat.st_size} bytes")
    print(f"Last Modified: {datetime.datetime.fromtimestamp(stat.st_mtime)}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order'")
        row = cursor.fetchone()
        if row:
            print("✅ TABLE FOUND: platform_ui_order")
            
            # Check content
            cursor.execute("PRAGMA table_info(platform_ui_order)")
            cols = [c[1] for c in cursor.fetchall()]
            print(f"   Columns: {cols}")
        else:
            print("❌ TABLE MISSING: platform_ui_order")
        conn.close()
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
else:
    print("❌ DB FILE NOT FOUND!")
