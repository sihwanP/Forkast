import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

print(f"--- Database Path in Settings: {settings.DATABASES['default']['NAME']} ---")
if os.path.exists(settings.DATABASES['default']['NAME']):
    print("✅ Database file exists.")
else:
    print("❌ Database file NOT found at settings path!")

try:
    admin_user = User.objects.get(username='admin')
    print(f"✅ User 'admin' FOUND.")
    print(f"   Email: {admin_user.email}")
    print(f"   Is Superuser: {admin_user.is_superuser}")
    print(f"   Is Staff: {admin_user.is_staff}")
    print(f"   Is Active: {admin_user.is_active}")
    print(f"   Password Hash starts with: {admin_user.password[:20]}...")
except User.DoesNotExist:
    print("❌ User 'admin' NOT FOUND in database.")

print("\n--- Direct SQLite Check ---")
conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
c = conn.cursor()
c.execute("SELECT username, is_superuser FROM auth_user WHERE username='admin'")
row = c.fetchone()
if row:
    print(f"SQLite Row found: {row}")
else:
    print("SQLite Row NOT found.")
conn.close()
