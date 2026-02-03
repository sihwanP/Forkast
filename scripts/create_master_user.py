import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

User = get_user_model()
username = 'master'
password = 'admin1234'

try:
    if User.objects.filter(username=username).exists():
        print(f"Deleting existing '{username}'...")
        User.objects.get(username=username).delete()

    print(f"Creating '{username}'...")
    User.objects.create_superuser(username, 'master@example.com', password)
    print(f"✅ SUCCESS: Created superuser '{username}' / '{password}'")
except Exception as e:
    print(f"❌ ERROR: {e}")
