import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append('c:/dev/Forkast')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.models import Order
from django.db import connection

def verify():
    print(f"--- Runtime Verification ---")
    print(f"Base Dir: {settings.BASE_DIR}")
    print(f"DB Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"DB Name (Settings): {settings.DATABASES['default']['NAME']}")
    
    # Check if file exists
    db_path = str(settings.DATABASES['default']['NAME'])
    print(f"DB File Exists: {os.path.exists(db_path)}")
    
    # Check actual table
    try:
        count = Order.objects.count()
        print(f"✅ ORM Success! Order Count: {count}")
    except Exception as e:
        print(f"❌ ORM Failed: {e}")
        
    # Check sqlite_master
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order'")
        row = cursor.fetchone()
        if row:
            print(f"✅ Table 'platform_ui_order' found in sqlite_master.")
        else:
            print(f"❌ Table 'platform_ui_order' NOT FOUND in sqlite_master.")

if __name__ == "__main__":
    verify()
