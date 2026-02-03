import os
import django
from django.test import RequestFactory
from django.conf import settings
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from platform_ui.views import index

class MockSession(dict):
    def get(self, key, default=None):
        return super().get(key, default)

try:
    print("--- Simulating Dashboard Request (Light) ---")
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    
    # Mock Session directly
    request.session = MockSession()
    request.session['is_working'] = True
    
    # Call View
    print("Calling index view...")
    response = index(request)
    print(f"Response Code: {response.status_code}")
    
    # Render
    if hasattr(response, 'render'):
        print("Rendering template...")
        response.render()
        print("✅ Template rendered successfully")
    
except Exception as e:
    error_msg = traceback.format_exc()
    print(f"❌ CRASH DETECTED:\n{error_msg}")
    with open('crash_log_light.txt', 'w', encoding='utf-8') as f:
        f.write(error_msg)
