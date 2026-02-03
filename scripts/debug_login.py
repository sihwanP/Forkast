import os
import django
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

# 1. Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

# 2. Info
print(f"--- Auth Debug Info ---")
print(f"DB Name: {settings.DATABASES['default']['NAME']}")
print(f"Auth User Model: {settings.AUTH_USER_MODEL}")
try:
    print(f"Auth Backends: {settings.AUTHENTICATION_BACKENDS}")
except:
    print("Auth Backends: Default")

# 3. Check User
User = get_user_model()
username = 'admin'
password = 'admin1234'

print(f"\n--- Checking User: {username} ---")
if User.objects.filter(username=username).exists():
    u = User.objects.get(username=username)
    print(f"User found: {u}")
    print(f"  is_active: {u.is_active}")
    print(f"  is_staff: {u.is_staff}")
    print(f"  is_superuser: {u.is_superuser}")
    print(f"  password hash: {u.password[:10]}...")
else:
    print("❌ User NOT found in DB!")

# 4. Test Authenticate
print(f"\n--- Testing authenticate() ---")
user = authenticate(username=username, password=password)
if user is not None:
    print("✅ AUTHENTICATION SUCCESS!")
    print(f"Returned user: {user}")
else:
    print("❌ AUTHENTICATION FAILED!")
    print("Possibilities: Wrong password, inactive user, or custom backend rejected it.")
