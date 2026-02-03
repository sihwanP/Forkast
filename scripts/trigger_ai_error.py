import os
import django
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.services_ai import generate_dashboard_analysis

print("--- TRIGGERING AI ANALYSIS ---")
try:
    # Dummy Data
    sales_data = {'revenue': 1000000, 'history': ["2023-10-01: 500000"]}
    weather_data = "Clear, 20C"
    inventory_data = "Item A: 10"
    event_data = "None"
    
    result = generate_dashboard_analysis(sales_data, weather_data, inventory_data, event_data)
    print("RESULT:", result)
except Exception as e:
    print("Runtime Error:", e)

print("--- CHECKING LOG FILE ---")
try:
    with open('ai_error.log', 'r', encoding='utf-8') as f:
        print(f.read())
except FileNotFoundError:
    print("ai_error.log not found (Maybe no error occurred?)")
