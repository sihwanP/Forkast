import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

User = get_user_model()
username = 'admin'
password = 'admin1234'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}")
    User.objects.create_superuser(username, email, password)
    print("✅ Superuser created.")
else:
    print("ℹ️ Superuser already exists. Resetting password...")
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print("✅ Password reset to default.")
