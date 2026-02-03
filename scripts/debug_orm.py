import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.models import Order
from django.db import connection

print(f"Active DB: {settings.DATABASES['default']['NAME']}")

try:
    # 1. Check Table Names through Django
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"All Tables: {tables}")
        
    # 2. Try ORM Access
    count = Order.objects.count()
    print(f"Order Count: {count}")
    print("✅ ORM Access Successful")
    
except Exception as e:
    print(f"❌ ORM Error: {e}")
