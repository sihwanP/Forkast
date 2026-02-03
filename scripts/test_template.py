import os
import django
from django.template.loader import render_to_string
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

print("--- TESTING TEMPLATE RENDER ---")

# Dummy Context replicating 'index' view structure
context = {
    'sales_today': None,
    'prediction_display': 1000000,
    'weather_obj': None,
    'inventory_items': [],
    'inventory_ctx': "Test Inventory",
    'latest_sentiment': None,
    'recent_posts': [],
    'is_working': True,
    'ai_loading': True,
    'ai_sales_analysis': "Analyzing...", # Added this as it is used in template
    'ai_strategy': [], # Added this
    'ai_cheer_msg': "Cheering..." # Added this
}

try:
    rendered = render_to_string('platform_ui/index.html', context)
    print("✅ Template Syntactically Correct. Render Length:", len(rendered))
except Exception as e:
    print("❌ TEMPLATE ERROR:")
    print(e)
