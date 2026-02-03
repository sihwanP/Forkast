import os
import django
from django.test import RequestFactory
from django.conf import settings
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from platform_ui.views import index

try:
    print("--- Simulating Dashboard Request ---")
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    
    # Simulate session
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session['is_working'] = True
    request.session.save()
    
    # Call View
    response = index(request)
    print(f"Response Code: {response.status_code}")
    print("✅ View executed successfully (No Crash)")
    
    # Try rendering content (if it's a template response)
    if hasattr(response, 'render'):
        print("Rendering template...")
        response.render()
        print("✅ Template rendered successfully")
    
except Exception as e:
    error_msg = traceback.format_exc()
    print(f"❌ CRASH DETECTED:\n{error_msg}")
    with open('crash_log.txt', 'w', encoding='utf-8') as f:
        f.write(error_msg)
