import os
import django
from django.conf import settings
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

try:
    # Attempt to render the FRESH template
    # We provide minimal dummy context to avoid VariableDoesNotExist causing issues (though usually it just warns)
    content = render_to_string('platform_ui/index_fresh.html', {
        'weather_obj': None,
        'sales_today': None,
        'recent_posts': [],
        'ai_loading': True
    })
    print("SUCCESS: Template rendered successfully.")
except Exception as e:
    print(f"FAILURE: {e}")
