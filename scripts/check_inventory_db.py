import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.models import Inventory
from django.conf import settings

print(f"DB PATH: {settings.DATABASES['default']['NAME']}")
count = Inventory.objects.count()
print(f"INVENTORY COUNT: {count}")
for item in Inventory.objects.all():
    print(f" - {item.item_name}: {item.current_stock}")
