import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

print("--- Checking via Django Connection ---")
with connection.cursor() as cursor:
    # 1. Get all tables
    tables = connection.introspection.table_names()
    print(f"Tables found: {tables}")
    
    # 2. Check for Member table
    if 'platform_ui_member' in tables:
        print("✅ 'platform_ui_member' exists.")
    else:
        print("❌ 'platform_ui_member' MISSING. Creating manually...")
        cursor.execute("""
            CREATE TABLE platform_ui_member (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                name varchar(100) NOT NULL,
                master_key varchar(50) NOT NULL UNIQUE,
                created_at datetime NOT NULL
            )
        """)
        print("✅ Created table via Raw SQL.")

# 3. Verify Model Access
from platform_ui.models import Member
import datetime

try:
    count = Member.objects.count()
    print(f"Current Member Count: {count}")
    
    if count == 0:
        Member.objects.create(name="Emergency Fix", master_key="999999")
        print("Created Emergency Member (Key: 999999)")
        
except Exception as e:
    print(f"❌ Model Access Error: {e}")
