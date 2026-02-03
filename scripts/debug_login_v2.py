import os
import django
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

def run():
    output = []
    
    # 1. Setup
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
    django.setup()

    # 2. Info
    output.append(f"--- Auth Debug Info ---")
    output.append(f"DB Name: {settings.DATABASES['default']['NAME']}")
    try:
        output.append(f"Auth Backends: {settings.AUTHENTICATION_BACKENDS}")
    except:
        output.append("Auth Backends: Default")

    # 3. Check User
    User = get_user_model()
    username = 'admin'
    password = 'admin1234'

    output.append(f"\n--- Checking User: {username} ---")
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        output.append(f"User found: {u}")
        output.append(f"  is_active: {u.is_active}")
        output.append(f"  is_staff: {u.is_staff}")
        output.append(f"  is_superuser: {u.is_superuser}")
        output.append(f"  password hash: {u.password[:10]}...")
    else:
        output.append("❌ User NOT found in DB!")

    # 4. Test Authenticate
    output.append(f"\n--- Testing authenticate() ---")
    user = authenticate(username=username, password=password)
    if user is not None:
        output.append("✅ AUTHENTICATION SUCCESS!")
        output.append(f"Returned user: {user}")
    else:
        output.append("❌ AUTHENTICATION FAILED!")
        output.append("Possibilities: Wrong password, inactive user, or check backend logic.")

    # Write to file
    with open('auth_result.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        with open('auth_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"CRITICAL ERROR: {e}")
