import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forkast_project.settings")
django.setup()

from platform_ui.models import DailySales, Inventory, Weather, LocalEvent, OwnerSentiment, CommunityPost

print("--- DEBUGGING DASHBOARD ---")
try:
    today = timezone.now().date()
    print(f"Date: {today}")

    print("Checking DailySales...")
    sales_today = DailySales.objects.filter(date=today).first()
    print(f"Sales: {sales_today}")

    print("Checking Inventory...")
    inventory_items = Inventory.objects.all()
    print(f"Inventory Count: {inventory_items.count()}")
    for i in inventory_items[:3]:
        print(f" - {i.item_name}: {i.current_stock}")

    print("Checking Weather...")
    weather_obj = Weather.objects.filter(date=today).first()
    print(f"Weather: {weather_obj}")

    print("Checking LocalEvent...")
    event_obj = LocalEvent.objects.filter(date=today).first()
    print(f"Event: {event_obj}")

    print("Checking OwnerSentiment...")
    latest_sentiment = OwnerSentiment.objects.last()
    print(f"Sentiment: {latest_sentiment}")

    print("Checking CommunityPost...")
    recent_posts = CommunityPost.objects.order_by('-created_at')[:3]
    print(f"Posts: {recent_posts.count()}")
    
    print("✅ All DB Queries Successful.")

except Exception as e:
    print(f"\n❌ CRASH DETECTED: {e}")
    import traceback
    traceback.print_exc()
