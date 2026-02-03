import os
import django
import sys

sys.path.append('c:/dev/Forkast')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.models import DailySales

count = DailySales.objects.count()
print(f"DailySales Count: {count}")
if count >= 30:
    print("SUCCESS: Data generated.")
else:
    print("FAILURE: Data not generated.")
