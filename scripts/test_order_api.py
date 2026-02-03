import os
import django
import json
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')
django.setup()

from platform_ui.models import Inventory, Order
from platform_ui.views import order_api

def test_order():
    # 1. Get a target item
    item = Inventory.objects.first()
    if not item:
        print("No inventory items found.")
        return

    initial_stock = item.current_stock
    print(f"Target: {item.item_name}")
    print(f"Initial Stock: {initial_stock}")
    print(f"Initial Status: {item.status}")

    # 2. Simulate Order Request (Order 50 items)
    order_qty = 50
    factory = RequestFactory()
    data = {'item_id': item.id, 'quantity': order_qty}
    request = factory.post('/api/order/', data=json.dumps(data), content_type='application/json')
    
    # 3. Call View
    response = order_api(request)
    print(f"API Response: {response.content.decode()}")

    # 4. Verify Update
    item.refresh_from_db()
    print(f"New Stock: {item.current_stock}")
    print(f"New Status: {item.status}")
    
    if item.current_stock == initial_stock + order_qty:
        print("✅ SUCCESS: Stock updated correctly.")
    else:
        print("❌ FAILURE: Stock did not update.")

    # 5. Check Order Record
    latest_order = Order.objects.filter(item=item).last()
    if latest_order and latest_order.quantity == order_qty:
         print(f"✅ SUCCESS: Order record created (ID: {latest_order.id}, Status: {latest_order.status})")
    else:
         print("❌ FAILURE: Order record not found.")

if __name__ == "__main__":
    test_order()
