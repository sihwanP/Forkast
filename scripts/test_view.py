import os
import django
from django.test import RequestFactory
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from platform_ui.views import index

print("--- TESTING VIEW LOGIC ---")
try:
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    
    # Mock Session
    class MockSession(dict):
        def save(self): pass
        
    request.session = MockSession()
    request.session['is_working'] = True
    
    # Run View
    response = index(request)
    print(f"✅ View Logic Passed. Status: {response.status_code}")
    
except Exception as e:
    print("❌ VIEW LOGIC ERROR:")
    print(e)
    import traceback
    traceback.print_exc()
