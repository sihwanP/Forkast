import os
import django
from django.contrib.auth import get_user_model

# 1. Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

# 2. Verify DB Path
from django.conf import settings
print(f"Target Database: {settings.DATABASES['default']['NAME']}")

# 3. Force Reset User
User = get_user_model()
username = 'master'
password = 'admin1234'
email = 'master@example.com'

try:
    # Delete if exists to ensure clean state
    if User.objects.filter(username=username).exists():
        print(f"⚠️ User '{username}' exists. Deleting...")
        User.objects.get(username=username).delete()
    
    # Create fresh
    print(f"✨ Creating new superuser '{username}'...")
    User.objects.create_superuser(username, email, password)
    print(f"✅ SUCCESS: Superuser created.\nID: {username}\nPW: {password}")

except Exception as e:
    print(f"❌ ERROR: {e}")
