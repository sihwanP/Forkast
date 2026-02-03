import os
import django
import sqlite3

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from django.conf import settings

print(f"--- Django Settings Verification ---")
db_path = settings.DATABASES['default']['NAME']
print(f"Django DB Path: {db_path}")
print(f"Absolute Path:  {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ CODE RED: The database file does NOT exist at this path!")
else:
    print("✅ Database file exists.")

print(f"\n--- SQLite Direct Inspection ---")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Found {len(tables)} tables.")
    
    if 'platform_ui_member' in tables:
        print("✅ Table 'platform_ui_member' EXISTS in this file.")
    else:
        print("❌ Table 'platform_ui_member' is MISSING in this file.")
        print(f"Tables found: {tables}")

    conn.close()
except Exception as e:
    print(f"Error inspecting DB: {e}")
