import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    if not User.objects.filter(username='master').exists():
        User.objects.create_superuser('master', 'master@example.com', 'admin1234')
        print("✅ Superuser 'master' created successfully.")
    else:
        print("ℹ️ Superuser 'master' already exists.")
except Exception as e:
    print(f"❌ Error creating superuser: {e}")
