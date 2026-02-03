import os
import django
import sys

# Setup Django environment
sys.path.append('c:/dev/Forkast')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.services_ai import get_gemini_response

print("--- Testing AI Connection ---")
try:
    response = get_gemini_response("Hello, are you working? Please reply with 'Yes, I am working'.")
    print(f"Response: {response}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
print("--- Test Complete ---")
