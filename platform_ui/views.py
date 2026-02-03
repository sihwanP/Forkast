from django.shortcuts import render, redirect
from .models import DailySales, Inventory, OwnerSentiment, CommunityPost, Weather, LocalEvent, AdminConfig, Member, Order
from django.utils import timezone
from datetime import timedelta
from .services_ai import analyze_sales_flow, suggest_operational_strategy, get_emotional_care_message, consult_ai, predict_revenue_with_ai
from .services_weather import fetch_real_time_weather

from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import login, get_user_model
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import random
import csv # [NEW]


# --- Sales Management ---
def sales_view(request):
    """
    Sales Management Dashboard with Sheets.
    Contains:
    1. Today's Hourly Sales (Real-time/Simulated)
    2. Past Sales History (Dummy 30 days)
    3. Predicted Sales (Dummy 7 days)
    4. Monthly Management (Aggregated)
    """
    import random
    from datetime import timedelta
    today = timezone.now().date()
    
    # 1. Today's Sales (Hourly) - Simulation based on current revenue
    sales_today_obj = DailySales.objects.filter(date=today).first()
    current_revenue = sales_today_obj.revenue if sales_today_obj else 0
    current_hour = timezone.now().hour
    
    hourly_sales_data = []
    # Distribute revenue vaguely into hours passed
    temp_total = 0
    weights = [
        0, 0, 0, 0, 0, 0, # 0-5
        1, 2, 5, 8, 5, 10, # 6-11
        20, 15, 8, 5, 8, 15, # 12-17
        25, 20, 15, 5, 2, 1  # 18-23
    ]
    
    valid_weights = weights[:current_hour+1]
    weight_sum = sum(valid_weights) if sum(valid_weights) > 0 else 1
    chunk = current_revenue / weight_sum
    
    running_total = 0
    for h in range(current_hour + 1):
        if h == current_hour:
             # Last hour gets the remainder to match exact total
             val = max(0, int(current_revenue - running_total))
        else:
             noise = random.uniform(0.8, 1.2)
             val = int(weights[h] * chunk * noise)
        
        running_total += val
        hourly_sales_data.append({
            'time': f"{h:02d}:00",
            'amount': val,
            'cumulative': running_total
        })
    
    # 2. Past Sales History (Dummy 30 Days)
    history_data = []
    for i in range(1, 31):
        d = today - timedelta(days=i)
        # Random daily revenue between 500k and 1.5m
        daily_rev = random.randint(500000, 1500000)
        # Cost approx 40%
        cost = int(daily_rev * 0.4)
        profit = daily_rev - cost
        history_data.append({
            'date': d,
            'day_of_week': d.strftime("%A"),
            'revenue': daily_rev,
            'cost': cost,
            'profit': profit
        })
    
    # 3. Predicted Sales (Next 7 Days)
    prediction_data = []
    for i in range(1, 8):
        d = today + timedelta(days=i)
        predicted_rev = random.randint(600000, 1400000)
        # Add some trend logic (e.g., weekends higher)
        if d.weekday() >= 5: # Sat, Sun
             predicted_rev = int(predicted_rev * 1.3)
        
        prediction_data.append({
            'date': d,
            'day_of_week': d.strftime("%A"),
            'predicted_revenue': predicted_rev,
            'weather_forecast': random.choice(['맑음', '흐림', '비', '눈']),
            'confidence': random.randint(85, 98)
        })

    # 4. Monthly Management (Current Month Aggregation)
    # Just summing up the dummy history for display
    monthly_total_revenue = sum(h['revenue'] for h in history_data)
    monthly_total_cost = sum(h['cost'] for h in history_data)
    monthly_total_profit = sum(h['profit'] for h in history_data)
    
    return render(request, 'platform_ui/sales.html', {
        'today': today,
        'current_revenue': current_revenue,
        'hourly_sales': hourly_sales_data,
        'history_data': history_data,
        'prediction_data': prediction_data,
        'monthly_stats': {
            'revenue': monthly_total_revenue,
            'cost': monthly_total_cost,
            'profit': monthly_total_profit
        }
    })

def index(request):
    # Security: Redirect to Cover if not working
    if not request.session.get('is_working', False):
        return redirect('cover')

    # 1. Fetch Basic Data (Fast DB only)
    today = timezone.now().date()
    
    # Fast DB Queries
    sales_today = DailySales.objects.filter(date=today).first()
    inventory_items = Inventory.objects.all()
    inventory_status_list = [f"{i.item_name}: {i.current_stock} ({i.status})" for i in inventory_items]
    inventory_ctx = ", ".join(inventory_status_list)
    
    # Basic Context from DB (No API calls)
    weather_obj = Weather.objects.filter(date=today).first() # Only read if exists
    event_obj = LocalEvent.objects.filter(date=today).first()
    latest_sentiment = OwnerSentiment.objects.last()
    recent_posts = CommunityPost.objects.order_by('-created_at')[:3]

    context = {
        'sales_today': sales_today,
        'prediction_display': sales_today.predicted_revenue if sales_today and sales_today.predicted_revenue else None,
        'weather_obj': weather_obj,
        'inventory_items': inventory_items[:5],
        'inventory_ctx': inventory_ctx,
        'latest_sentiment': latest_sentiment,
        'recent_posts': recent_posts,
        'is_working': True,
        # AI Data -> Will be loaded via AJAX
        'ai_loading': True 
    }
    return render(request, 'platform_ui/index_v2.html', context)

def dashboard_stats_api_v2(request):
    """
    API Endpoint for heavy AI/Weather operations.
    Called via AJAX after page load.
    """
    try:
        today = timezone.now().date()
        
        # 1. Weather Update (Heavy HTTP)
        real_cond, real_temp = fetch_real_time_weather()
        if real_cond is not None:
             Weather.objects.update_or_create(
                date=today,
                defaults={'condition': real_cond, 'temperature': real_temp}
            )
        
        # 2. Context Building
        from django.db.models import Sum
        sales_today_agg = DailySales.objects.filter(date=today).aggregate(total_revenue=Sum('revenue'))
        today_revenue = sales_today_agg['total_revenue'] or 0
        
        history_start = today - timedelta(days=30)
        sales_history_qs = DailySales.objects.filter(date__gte=history_start)\
            .values('date').annotate(total_revenue=Sum('revenue')).order_by('date')
        
        sales_history = [f"{s['date'].strftime('%Y-%m-%d')}: {s['total_revenue']}원" for s in sales_history_qs]
        
        inventory_items = Inventory.objects.all()
        inventory_ctx = ", ".join([f"{i.item_name}: {i.current_stock}" for i in inventory_items])
        
        weather_ctx = f"{real_cond}, {real_temp}도" if real_cond else "맑음, 20도"
        event_obj = LocalEvent.objects.filter(date=today).first()
        event_ctx = f"{event_obj.name}" if event_obj else "특이사항 없음"

        # 3. AI Prediction & Analysis (Unified Single Call)
        sales_ctx = {
            'revenue': today_revenue,
            'history': sales_history
        }

        # [NEW] Simulate Hourly Sales Distribution (Peak: 12-13, 18-20)
        import random
        hourly_sales = [0] * 24
        current_hour = timezone.now().hour
        total_revenue = today_revenue
        
        # Distribute revenue vaguely
        if total_revenue > 0:
            weights = [
                0, 0, 0, 0, 0, 0, # 0-5
                1, 2, 5, 8, 5, 10, # 6-11
                20, 15, 8, 5, 8, 15, # 12-17
                25, 20, 15, 5, 2, 1  # 18-23
            ]
            # Normalize to current hour
            valid_weights = weights[:current_hour+1]
            total_weight = sum(valid_weights)
            
            if total_weight > 0:
                chunk = total_revenue / total_weight
                for h in range(current_hour + 1):
                    # Add some randomness (+/- 20%)
                    noise = random.uniform(0.8, 1.2)
                    val = int(weights[h] * chunk * noise)
                    hourly_sales[h] = val

        # [NEW] Generate 30-Day Past Sales Data for Dashboard Chart
        past_sales_data = []
        past_dates = []
        # Simple simulation: 30 days ago to yesterday
        for i in range(30, 0, -1):
             d = today - timedelta(days=i)
             # Random revenue 500k ~ 1.5m
             rev = random.randint(500000, 1500000)
             # Boost for Fri/Sat
             if d.weekday() >= 4: # Fri, Sat, Sun
                 rev = int(rev * 1.3)
             
             past_sales_data.append(rev)
             past_dates.append(d.strftime('%m/%d'))

        # [NEW] AI Comparison Logic for Emotional Care Message
        if past_sales_data:
            avg_past_sales = sum(past_sales_data) / len(past_sales_data)
        else:
            avg_past_sales = 0
            
        current_rev = sales_today.revenue if sales_today else 0
        
        # Determine Message based on Comparison
        # Determine Message based on Comparison
        if current_rev > avg_past_sales:
            diff = int(current_rev - avg_past_sales)
            final_cheer_msg = (
                f"🎉 축하합니다! 지난 30일 평균보다 {diff:,}원 더 높은 매출을 달성하셨네요. "
                "사장님의 열정과 노력이 결실을 맺고 있습니다. 정말 자랑스럽습니다!"
            )
            past_analysis_msg = f"지난달 평균 대비 {diff:,}원 증가했습니다."
        else:
            diff = int(avg_past_sales - current_rev)
            final_cheer_msg = (
                f"🌿 오늘은 평균보다 조금 조용한 하루네요. ({diff:,}원 차이) "
                "하지만 괜찮습니다. 사장님의 꾸준함은 결국 빛을 발할 거예요. "
                "잠시 따뜻한 차 한 잔으로 숨을 고르시는 건 어떨까요?"
            )
            past_analysis_msg = f"지난달 평균 대비 {diff:,}원 감소했습니다."

        from .services_ai import generate_dashboard_analysis
        ai_result = generate_dashboard_analysis(sales_ctx, weather_ctx, inventory_ctx, event_ctx)

        return JsonResponse({
            'status': 'success',
            'weather': {'condition': real_cond, 'temp': real_temp},
            'prediction': ai_result.get('prediction', 0),
            'analysis': ai_result.get('analysis', "분석 대기 중"),
            'strategies': ai_result.get('strategies', []),
            'cheer_msg': final_cheer_msg, # [MODIFIED] Use our logic-based message
            # 'cheer_msg': ai_result.get('cheer_msg', "파이팅!"),
            'hourly_sales': hourly_sales,
            'past_sales': {'dates': past_dates, 'revenues': past_sales_data}, # [NEW]
            'past_analysis': past_analysis_msg # [NEW]
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e) + " [DEBUG CHECK]"})


def cover(request):
    """
    Landing page (Cover).
    """
    if request.session.get('is_working', False):
        return redirect('dashboard')
    
    return render(request, 'platform_ui/cover.html')

def verify_admin(request):
    """
    Checks the admin key.
    """
    if request.method == "POST":
        input_key = request.POST.get('admin_key')
        
        # Get or create correct key
        config, created = AdminConfig.objects.get_or_create(id=1)
        
        if input_key == config.key:
            # Login Success
            request.session['is_working'] = True
            request.session.modified = True
            return redirect('dashboard')
        else:
            # Login Failed
            return render(request, 'platform_ui/cover.html', {'error_msg': 'Incorrect Admin Key'})
    
    return redirect('cover')

def super_admin(request):
    """
    Super Admin Dashboard: Requires Oracle DB Login.
    Displays Sales History and Member Management.
    """
    # [ENHANCED FLOW] Ensure standard Django Admin login first
    if not request.user.is_authenticated or not request.user.is_staff:
        from django.contrib.admin.views.decorators import staff_member_required
        return redirect('/admin/login/?next=' + request.path)

    import oracledb
    
    # 1. Handle Logout Check (Internal session)
    if not request.session.get('is_super_admin', False):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            # [ENHANCED LOGIN] First check if it's the requested 'master' account
            if username == 'master' and password == 'master1234':
                request.session['is_super_admin'] = True
                request.session['super_admin_user'] = username
                return redirect('super_admin')

            # Attempt to connect to Oracle with these credentials
            try:
                # Use the same connection params as settings.py but with user input
                conn = oracledb.connect(
                    user=username,
                    password=password,
                    host='localhost',
                    port=1521,
                    service_name='xe'
                )
                conn.close()
                # Success! Set session
                request.session['is_super_admin'] = True
                request.session['super_admin_user'] = username
                return redirect('super_admin')
            except Exception as e:
                return render(request, 'platform_ui/super_admin_login.html', {
                    'error': f"Oracle 접속 실패: {str(e)}"
                })
        
        # Render Login Page
        return render(request, 'platform_ui/super_admin_login.html')

    # 2. Authenticated Dashboard Logic
    if request.method == "POST":
        # Handle Member Management (Add/Delete)
        if 'add_member' in request.POST:
            name = request.POST.get('name')
            master_key = request.POST.get('master_key')
            if name and master_key:
                try: Member.objects.create(name=name, master_key=master_key)
                except: pass
        elif 'delete_member' in request.POST:
            member_id = request.POST.get('member_id')
            Member.objects.filter(id=member_id).delete()
        
        # --- NEW: Inventory & Order Management handlers ---
        elif 'update_inventory' in request.POST:
            item_id = request.POST.get('item_id')
            new_stock = int(request.POST.get('current_stock'))
            item = Inventory.objects.get(id=item_id)
            item.current_stock = new_stock
            
            # Recalculate Status
            ratio = item.current_stock / item.optimal_stock if item.optimal_stock > 0 else 0
            if ratio < 0.3: item.status = 'LOW'
            elif ratio > 1.5: item.status = 'OVER'
            else: item.status = 'GOOD'
            item.save()
            
        elif 'confirm_order' in request.POST:
            order_id = request.POST.get('order_id')
            order = Order.objects.get(id=order_id)
            if order.status == 'PENDING':
                # Update Store Inventory (Synchronization)
                item = order.item
                item.current_stock += order.quantity
                
                # Recalculate Status
                ratio = item.current_stock / item.optimal_stock if item.optimal_stock > 0 else 0
                if ratio < 0.3: item.status = 'LOW'
                elif ratio > 1.5: item.status = 'OVER'
                else: item.status = 'GOOD'
                item.save()
                
                # Mark Order as Completed
                order.status = 'COMPLETED'
                order.save()

        elif 'delete_order' in request.POST:
            order_id = request.POST.get('order_id')
            Order.objects.filter(id=order_id).delete()

        # --- LOGISTICS INTEGRATION HANDLERS (Oracle Synced) ---
        from django.db import connection
        action_type = request.POST.get('action_type')
        
        if action_type == 'reg_inbound':
            item_id = request.POST.get('item_id')
            qty = int(request.POST.get('quantity', 0))
            if item_id and qty > 0:
                item = Inventory.objects.get(id=item_id)
                item.current_stock += qty
                # Status calc
                ratio = item.current_stock / item.optimal_stock if item.optimal_stock > 0 else 1.0
                if ratio < 0.3: item.status = 'LOW'
                elif ratio > 1.5: item.status = 'OVER'
                else: item.status = 'GOOD'
                item.save()
                
                # Oracle Sync: Update Inventory in Oracle
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE PLATFORM_UI_INVENTORY SET CURRENT_STOCK = :stock, STATUS = :status WHERE ID = :id",
                        {'stock': item.current_stock, 'status': item.status, 'id': item.id}
                    )

        elif action_type == 'reg_order':
            item_id = request.POST.get('item_id')
            qty = int(request.POST.get('quantity', 0))
            if item_id and qty > 0:
                item = Inventory.objects.get(id=item_id)
                order = Order.objects.create(item=item, quantity=qty, status='PENDING')
                
                # Oracle Sync: Insert Order into Oracle
                with connection.cursor() as cursor:
                    # Note: Oracle sequence/ID handling might be needed if not auto-managed by Django
                    cursor.execute(
                        "INSERT INTO PLATFORM_UI_ORDER (ITEM_ID, QUANTITY, STATUS, CREATED_AT) VALUES (:item_id, :qty, 'PENDING', CURRENT_TIMESTAMP)",
                        {'item_id': item.id, 'qty': qty}
                    )

        elif action_type == 'reg_procure':
            item_id = request.POST.get('item_id')
            qty = int(request.POST.get('quantity', 0))
            if item_id and qty > 0:
                item = Inventory.objects.get(id=item_id)
                item.current_stock += qty
                item.save()
                
                # Oracle Sync: Update Inventory in Oracle (Procurement)
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE PLATFORM_UI_INVENTORY SET CURRENT_STOCK = :stock WHERE ID = :id",
                        {'stock': item.current_stock, 'id': item.id}
                    )

        elif action_type == 'reg_statement':
            target = request.POST.get('target_name')
            amount = request.POST.get('total_amount')
            remarks = request.POST.get('remarks')
            # Transaction recording conceptual (Optional sync if Statement table exists in Oracle)
            print(f"ORACLE SYNC (LOG): TRANSACTION RECORDED: {target} | Amount: {amount} | Remarks: {remarks}")

        elif 'toggle_permission' in request.POST:
            member_id = request.POST.get('member_id')
            member = Member.objects.get(id=member_id)
            member.is_approved = not member.is_approved
            member.save()
            
        return redirect('super_admin')

    # Fetch Data for SCM Console
    inventory = Inventory.objects.all().order_by('item_name')
    orders = Order.objects.all().order_by('-created_at')
    members = Member.objects.all().order_by('-created_at')
    
    # KPI Calculations
    low_stock_count = Inventory.objects.filter(status='LOW').count()
    pending_orders_count = Order.objects.filter(status='PENDING').count()
    
    return render(request, 'platform_ui/super_admin.html', {
        'members': members,
        'inventory': inventory,
        'orders': orders,
        'low_stock_count': low_stock_count,
        'pending_orders_count': pending_orders_count,
        'admin_user': request.session.get('super_admin_user'),
        'filters': {
            'product_name': request.GET.get('product_name', '')
        }
    })

def super_admin_logout(request):
    """Logout super admin session."""
    request.session['is_super_admin'] = False
    request.session['super_admin_user'] = None
    return redirect('super_admin')

def change_admin_key(request):
    """
    Changes the admin key (Requires Valid Master Key from ANY Member).
    """
    if request.method == "POST":
        master_key_input = request.POST.get('master_key')
        new_key = request.POST.get('new_key')
        
        # Runtime DB Fix for Member Table
        from django.db import connection
        try:
            is_valid_master = Member.objects.filter(master_key=master_key_input).exists()
        except:
             # If Table missing, create it (Self-Healing)
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS platform_ui_member (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name varchar(100) NOT NULL,
                        master_key varchar(50) NOT NULL UNIQUE,
                        created_at datetime NOT NULL
                    )
                """)
            is_valid_master = False # Newly created table has no keys yet

        if is_valid_master and new_key:
            # Use update() to only touch the 'key' column, avoiding 'no such column: master_key' error
            # if the DB schema is out of sync regarding the legacy master_key column.
            AdminConfig.objects.update_or_create(id=1, defaults={'key': new_key})
            return redirect('cover')
        else:
            return render(request, 'platform_ui/cover.html', {'error_msg': 'Invalid Master Key or Member DB Error.'})
            
    return redirect('cover')

def reset_admin_key(request):
    """
    Resets the admin key to default 'admin' (Requires Valid Master Key).
    """
    if request.method == "POST":
        master_key_input = request.POST.get('master_key')
        
        try:
            is_valid_master = Member.objects.filter(master_key=master_key_input).exists()
        except:
             # If Table missing, create it
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS platform_ui_member (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name varchar(100) NOT NULL,
                        master_key varchar(50) NOT NULL UNIQUE,
                        created_at datetime NOT NULL
                    )
                """)
            is_valid_master = False

        if is_valid_master:
            # Use update_or_create to safely set the key
            AdminConfig.objects.update_or_create(id=1, defaults={'key': "admin"})
            return redirect('cover')
        else:
            return render(request, 'platform_ui/cover.html', {'error_msg': 'Invalid Master Key.'})
        
    return redirect('cover')

def toggle_work_status(request):
    request.session['is_working'] = False
    request.session.modified = True 
    return redirect('cover')

# --- Inventory Management ---

def inventory_view(request):
    """
    Renders the inventory management page.
    """
    items = Inventory.objects.all().order_by('item_name')
    
    # EMERGENCY SELF-HEALING: If DB is empty, populate it right here
    if not items.exists():
        print("VIEW DEBUG: Inventory empty. Auto-generating default items...")
        defaults = [
            {"name": "염지 닭 (10호)", "optimal": 50},
            {"name": "치킨 파우더 (10kg)", "optimal": 10},
            {"name": "식용유 (18L)", "optimal": 5},
            {"name": "양념 소스 (10kg)", "optimal": 5},
            {"name": "치킨 무 (Box)", "optimal": 20},
            {"name": "콜라 1.25L", "optimal": 60},
            {"name": "포장용 박스", "optimal": 100},
            {"name": "나무 젓가락", "optimal": 200},
        ]
        import random
        for d in defaults:
            current = int(d["optimal"] * random.uniform(0.4, 1.2))
            ratio = current / d["optimal"]
            Inventory.objects.create(
                item_name=d["name"],
                current_stock=current,
                optimal_stock=d["optimal"],
                status='GOOD' # Default status
            )
        # Re-fetch after creation
        items = Inventory.objects.all().order_by('item_name')

    # [SELF-HEALING] Runtime Check for Order Table
    from django.db import connection, transaction
    try:
        with connection.cursor() as cursor:
            # Check existencelogic
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_ui_order'")
            if not cursor.fetchone():
                print("🚨 VIEW HEALING: 'platform_ui_order' missing. Creating now...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "platform_ui_order" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "quantity" integer NOT NULL,
                        "status" varchar(20) NOT NULL,
                        "created_at" datetime NOT NULL,
                        "item_id" integer NOT NULL REFERENCES "platform_ui_inventory" ("id") DEFERRABLE INITIALLY DEFERRED
                    );
                """)
                cursor.execute('CREATE INDEX IF NOT EXISTS "platform_ui_order_item_id_idx" ON "platform_ui_order" ("item_id");')
                # Fake migration to prevent future conflicts
                cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('platform_ui', '0005_order', datetime('now'));")
                print("✅ VIEW HEALING: Table created successfully.")
            else:
                pass # Table exists
    except Exception as e:
        print(f"❌ VIEW HEALING FAILED: {e}")

    # Fetch Pending Orders
    pending_orders = []
    try:
         pending_orders = Order.objects.filter(status='PENDING').order_by('-created_at')
         # Force query execution to ensure table is readable
         list(pending_orders)
    except Exception as query_e:
        print(f"⚠️ Query failed even after healing: {query_e}")
        pending_orders = []

    return render(request, 'platform_ui/inventory.html', {
        'inventory_items': items,
        'pending_orders': pending_orders
    })

@csrf_exempt
def inventory_api(request):
    """
    API for adding, updating, and deleting inventory items.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            
            # Determine Status
            current = int(data['current_stock'])
            optimal = int(data['optimal_stock'])
            ratio = current / optimal if optimal > 0 else 0
            
            if ratio < 0.3: status = 'LOW'
            elif ratio > 1.5: status = 'OVER'
            else: status = 'GOOD'

            if item_id: # Update
                item = Inventory.objects.get(id=item_id)
                item.item_name = data['item_name']
                item.current_stock = current
                item.optimal_stock = optimal
                item.status = status
                item.save()
            else: # Create
                Inventory.objects.create(
                    item_name=data['item_name'],
                    current_stock=current,
                    optimal_stock=optimal,
                    status=status
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            Inventory.objects.get(id=data['id']).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def order_api(request):
    """
    API for handling orders.
    POST: Create Order (Status: PENDING) - No Stock Update
    PUT: Confirm Order (Status: PENDING -> COMPLETED) - Update Stock
    """
    from .models import Order # Import here to avoid circular/top-level issues if any
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity'))
            
            # 1. Create Order (Pending)
            item = Inventory.objects.get(id=item_id)
            Order.objects.create(
                item=item,
                quantity=quantity,
                status='PENDING'
            )
            return JsonResponse({'status': 'success', 'message': '수주 요청이 접수되었습니다. (입고 대기)'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            
            order = Order.objects.get(id=order_id)
            if order.status != 'PENDING':
                return JsonResponse({'status': 'error', 'message': '이미 처리된 주문 내역입니다.'})

            # 2. Update Stock
            item = order.item
            item.current_stock += order.quantity
            
            # 3. Recalculate Status
            ratio = item.current_stock / item.optimal_stock if item.optimal_stock > 0 else 0
            if ratio < 0.3: item.status = 'LOW'
            elif ratio > 1.5: item.status = 'OVER'
            else: item.status = 'GOOD'
            item.save()
            
            # 4. Mark Order Complete
            order.status = 'COMPLETED'
            order.save()
            
            return JsonResponse({'status': 'success', 'message': '입고 처리가 완료되었습니다.'})

        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
def generate_pos_data(request):
    """
    Simulates a new transaction and DEDUCTS INVENTORY.
    """
    if request.method == 'POST':
        try:
            # 1. Update Daily Sales
            today = timezone.now().date()
            sales_entry, created = DailySales.objects.get_or_create(date=today, defaults={'revenue': 0, 'predicted_revenue': 0})
            
            # Add random transaction amount
            transaction = random.choice([5000, 8000, 12000, 25000, 40000])
            sales_entry.revenue += transaction
            sales_entry.save()

            # 2. Simulate Inventory Deduction (Real-time update)
            # Randomly deduct 1-3 items per transaction
            all_items = list(Inventory.objects.all())
            if all_items:
                deduct_items = random.sample(all_items, k=min(len(all_items), random.randint(1, 3)))
                for item in deduct_items:
                    deduct_qty = random.randint(1, 5)
                    item.current_stock = max(0, item.current_stock - deduct_qty)
                    
                    # Update status
                    ratio = item.current_stock / item.optimal_stock if item.optimal_stock > 0 else 0
                    if ratio < 0.3: item.status = 'LOW'
                    elif ratio > 1.5: item.status = 'OVER'
                    else: item.status = 'GOOD'
                    
                    item.save()

            return JsonResponse({
                'status': 'success', 
                'new_revenue': sales_entry.revenue,
                'deducted_items': [item.item_name for item in deduct_items] if all_items else []
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})
def force_master_login(request):
    """
    DEBUG TOOL: Force creates 'master' superuser and logs them in.
    """
    User = get_user_model()
    username = 'master'
    password = 'master1234'
    
    # 1. Debug DB Path
    db_path = settings.DATABASES['default']['NAME']
    
    try:
        # 2. Ensure User Exists (In THIS server process)
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            created = False
        else:
            user = User.objects.create_superuser(username, 'master@test.com', password)
            created = True
            
        # 3. Force Backend (Required for programmatic login)
        if not hasattr(user, 'backend'):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
        # 4. Perform Login
        login(request, user)
        
        return HttpResponse(f"""
            <h1>✅ Login Forced Successfully</h1>
            <p><b>User:</b> {user.username}</p>
            <p><b>Password:</b> {password}</p>
            <p><b>DB Path:</b> {db_path}</p>
            <p><b>Status:</b> {{'Created' if created else 'Updated'}}</p>
            <p>You are now authenticated. <a href='/admin/'>Go to Admin Page</a></p>
        """)
    except Exception as e:
        return HttpResponse(f"<h1>❌ Error</h1><p>{{str(e)}}</p>")

@csrf_exempt
def upload_csv_api(request):
    """
    API to upload CSV and analyze detailed sales data.
    Format: Order Date, Item Name, Time, Price, Quantity
    """
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            hourly_revenue = {} 
            item_sales = {} 
            daily_agg = {} # {date_obj: revenue}
            total_items = 0
            
            # Helper to parse date
            def parse_date_str(d_str):
                d_str = d_str.strip()
                for fmt in ('%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d'):
                    try:
                        return timezone.datetime.strptime(d_str, fmt).date()
                    except ValueError:
                        continue
                return timezone.now().date() # Fallback

            # Aggregation by (date, item_name) to support detailed records
            daily_item_agg = {} # {(date, item_name): revenue}
            
            for row in reader:
                row_keys = list(row.keys())
                
                time_key = next((k for k in row_keys if "Time" in k or "시간" in k), None)
                price_key = next((k for k in row_keys if "Price" in k or "가격" in k), None)
                qty_key = next((k for k in row_keys if "Quantity" in k or "수량" in k), None)
                item_key = next((k for k in row_keys if "Item" in k or "상품" in k), None) 
                date_key = next((k for k in row_keys if "Date" in k or "날짜" in k), None)
                
                # Fallback indices
                if not (time_key and price_key and qty_key and item_key):
                    if len(row_keys) >= 5:
                         date_key = row_keys[0]; time_key = row_keys[2]; price_key = row_keys[3]; qty_key = row_keys[4]; item_key = row_keys[1] 
                    else: continue

                raw_time = row[time_key].strip()
                item_name = row[item_key].strip()
                raw_date = row.get(date_key, str(timezone.now().date())) 
                
                # Clean Price/Qty
                import re
                clean_price_str = re.sub(r'[^\d.]', '', row[price_key])
                if not clean_price_str: continue
                price = int(float(clean_price_str))
                
                clean_qty_str = re.sub(r'[^\d.]', '', row[qty_key])
                if not clean_qty_str: continue
                qty = int(float(clean_qty_str))
                
                revenue = price * qty
                total_items += qty
                
                # Aggregate/Process Date
                p_date = parse_date_str(raw_date)
                if p_date not in daily_agg: daily_agg[p_date] = 0
                daily_agg[p_date] += revenue
                
                # Item-wise aggregation
                key = (p_date, item_name)
                daily_item_agg[key] = daily_item_agg.get(key, 0) + revenue

                # Hourly Aggregation
                hour_part = raw_time.split(':')[0]
                normalized_time = f"{hour_part}:00"
                hourly_revenue[normalized_time] = hourly_revenue.get(normalized_time, 0) + revenue
                    
                # Item Aggregation 
                if item_name not in item_sales:
                    item_sales[item_name] = {'qty': 0, 'revenue': 0}
                item_sales[item_name]['qty'] += qty
                item_sales[item_name]['revenue'] += revenue
            
            # DB Update: Overwrite mode using (date, item_name) as identifier
            for (d, item), rev in daily_item_agg.items():
                obj, created = DailySales.objects.get_or_create(
                    date=d,
                    item_name=item,
                    defaults={
                        'revenue': rev,
                        'predicted_revenue': 0
                    }
                )
                if not created:
                    obj.revenue = rev
                    obj.save()

            # Store in Session
            request.session['current_item_sales'] = item_sales
            request.session['current_total_sales'] = sum(hourly_revenue.values())
            
            labels = sorted(hourly_revenue.keys())
            values = [hourly_revenue[k] for k in labels]
            total = sum(values)
            
            # Return Min/Max for Frontend auto-date set
            dates_found = list(daily_agg.keys())
            min_date = min(dates_found) if dates_found else None
            max_date = max(dates_found) if dates_found else None

            # Generate Cheer Msg
            if total < 500000:
                cheer_msg = f"조금 조용한 하루였지만, 사장님의 정성은 손님들에게 닿았을 거예요. 내일은 더 좋은 결과가 있을 겁니다! 힘내세요 💪 ({total:,}원)"
            else:
                cheer_msg = f"오늘 하루도 수고 많으셨습니다! 매출 {total:,}원 달성을 축하드려요. 사장님의 노력이 빛나는 순간입니다! 🌸"
            
            return JsonResponse({
                'status': 'success',
                'labels': labels,
                'data': values,
                'total_revenue': total,
                'total_orders': total_items,
                'cheer_msg': cheer_msg,
                'min_date': min_date,
                'max_date': max_date,
                'analysis': f"분석 완료: 총 주문 {total_items}건, 매출 {total:,}원 집계됨."
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"처리 실패: {str(e)}"})
            
    return JsonResponse({'status': 'error', 'message': '파일 없음'}, status=400)

@csrf_exempt
def upload_past_csv_api(request):
    """
    API to upload PAST CSV (1 Year) and compare with stored CURRENT session data.
    Logic: Comparison Standard = ONE MONTH.
    - Past: Extract Monthly Average (Total / Months).
    - Current: Project to Monthly if duration < 5 days (e.g. Daily * 30).
    """
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            csv_file = request.FILES['file']
            # Decode carefully
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
            except UnicodeDecodeError:
                # Retry with cp949 (korean euc-kr)
                csv_file.seek(0)
                decoded_file = csv_file.read().decode('cp949').splitlines()

            reader = csv.DictReader(decoded_file)
            
            past_item_sales = {}
            past_total_revenue = 0
            past_months = set() # To count months
            row_idx = 0
            
            for row in reader:
                row_idx += 1
                try:
                    # Robust key finding
                    row_keys = list(row.keys())
                    
                    price_key = next((k for k in row_keys if k and ("Price" in k or "가격" in k)), None)
                    qty_key = next((k for k in row_keys if k and ("Quantity" in k or "수량" in k)), None)
                    item_key = next((k for k in row_keys if k and ("Item" in k or "상품" in k)), None)
                    date_key = next((k for k in row_keys if k and ("Date" in k or "날짜" in k)), None)
                    
                    # Fallback by index
                    if not (price_key and qty_key and item_key):
                        if len(row_keys) >= 5:
                            date_key = row_keys[0] # Order Date
                            item_key = row_keys[1]
                            price_key = row_keys[3]
                            qty_key = row_keys[4]
                        else: continue

                    raw_price = row.get(price_key, '')
                    raw_qty = row.get(qty_key, '')
                    raw_item = row.get(item_key, '')
                    raw_date = row.get(date_key, '')
                    
                    if not raw_price or not raw_qty: continue
                    
                    import re
                    clean_price = re.sub(r'[^\d.]', '', str(raw_price))
                    clean_qty = re.sub(r'[^\d.]', '', str(raw_qty))
                    
                    if not clean_price or not clean_qty: continue
                    
                    revenue = int(float(clean_price)) * int(float(clean_qty))
                    item_name = str(raw_item).strip()
                    
                    past_total_revenue += revenue
                    
                    if item_name not in past_item_sales:
                        past_item_sales[item_name] = 0
                    past_item_sales[item_name] += revenue
                    
                    # Date Tracking (YYYY-MM)
                    try:
                         # Assume format YYYY-MM-DD
                         if raw_date and len(raw_date) >= 7:
                             past_months.add(raw_date[:7]) 
                    except: pass
                    
                except Exception as row_e:
                    print(f"Row {row_idx} Error: {row_e}")
                    continue

            # --- Monthly Average Comparison Logic ---
            current_item_sales = request.session.get('current_item_sales', {})
            current_total = request.session.get('current_total_sales', 0)
            
            # Check Session
            if not current_item_sales and current_total == 0:
                 return JsonResponse({'status': 'error', 'message': '현재 매출 데이터가 없습니다. 먼저 [오늘 실시간 분석]에서 파일을 업로드해주세요.'})

            # 1. Calculate Past Monthly Average
            num_past_months = len(past_months) if past_months else 12 # Default to 12 if date parsing fails but file is large
            if num_past_months == 0: num_past_months = 1
            
            past_monthly_avg = int(past_total_revenue / num_past_months)
            
            # 2. Project Current to Monthly (Simple Heuristic)
            # We assume current is "Daily" if it's small relative to standard chicken monthly sales or if we knew date range.
            # Here we simplify: assume current upload is "1 Day" as per user context.
            projected_current_monthly = current_total * 30
            
            # 3. Gap Calculation
            gap = projected_current_monthly - past_monthly_avg
            gap_str = f"{abs(gap):,}원 {'증가' if gap >= 0 else '감소'}"
            growth_rate = ((projected_current_monthly - past_monthly_avg) / past_monthly_avg * 100) if past_monthly_avg > 0 else 0
            
            # 4. Item Comparison (Projected Current Item Sales vs Past Item Avg)
            past_item_avg = {k: int(v / num_past_months) for k, v in past_item_sales.items()}
            
            dropped_items = []
            for name, past_avg in past_item_avg.items():
                curr_daily = current_item_sales.get(name, {}).get('revenue', 0)
                curr_proj = curr_daily * 30
                if curr_proj < past_avg:
                    diff = past_avg - curr_proj
                    dropped_items.append((name, diff))
            
            dropped_items.sort(key=lambda x: x[1], reverse=True) 

            # 5. Generate Message
            analysis_text = f"📊 **월 매출 예측 분석 (기준: 30일 환산)**\n\n"
            analysis_text += f"오늘 매출 추세를 지속할 경우, 예상 월 매출은 **{projected_current_monthly:,}원**입니다.\n"
            analysis_text += f"> 작년 월평균({past_monthly_avg:,}원) 대비 **{growth_rate:.1f}% {gap_str}**할 것으로 예측됩니다.\n\n"
            
            if dropped_items:
                top_drop = dropped_items[0]
                analysis_text += f"⚠️ **주요 관리 대상**: '{top_drop[0]}'\n"
                analysis_text += f"과거 월평균 대비 약 **{top_drop[1]:,}원** 저조할 것으로 예상됩니다. 판매 촉진 전략이 필요합니다."
            else:
                analysis_text += "🚀 **긍정적 신호**: 모든 메뉴가 작년 월평균 실적을 상회하고 있습니다. 현재의 운영 전략을 유지하세요!"

            # 6. Pie Chart Data (Show Past MONTHLY AVG distribution)
            pie_labels = list(past_item_avg.keys())
            pie_values = list(past_item_avg.values())

            return JsonResponse({
                'status': 'success',
                'analysis': analysis_text,
                'pie_labels': pie_labels,
                'pie_data': pie_values,
                'total_revenue': projected_current_monthly, # Assuming this is the relevant 'total_revenue' for this context
                'total_orders': None # No direct 'total_orders' calculated in this function, setting to None or could be derived if needed
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f"서버 에러: {str(e)}"})
            
    return JsonResponse({'status': 'error', 'message': '파일 없음'}, status=400)

@csrf_exempt
def sales_period_stats_api(request):
    """
    API to fetch DailySales statistics for a specific date range.
    GET params: start_date, end_date (YYYY-MM-DD)
    """
    try:
        start_str = request.GET.get('start_date')
        end_str = request.GET.get('end_date')

        if not start_str or not end_str:
            # Default to last 7 days if not provided
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=6)
        else:
            start_date = timezone.datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_str, '%Y-%m-%d').date()

        # Query Database with Aggregation
        from django.db.models import Sum
        sales_data = DailySales.objects.filter(date__range=[start_date, end_date])\
            .values('date').annotate(total_revenue=Sum('revenue')).order_by('date')
        
        labels = [s['date'].strftime('%Y-%m-%d') for s in sales_data]
        values = [s['total_revenue'] for s in sales_data]
        
        total_revenue = sum(values)
        avg_revenue = int(total_revenue / len(values)) if values else 0

        # Create Highcharts-friendly format
        return JsonResponse({
            'status': 'success',
            'labels': labels,
            'data': values,
            'summary': {
                'total_revenue': total_revenue,
                'avg_revenue': avg_revenue,
                'days_count': len(values)
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# --- MPA Views ---

def dashboard(request):
    """Main Dashboard View"""
    # Context logic similar to index but focused on dashboard
    context = {}
    
    # 1. Weather
    try:
        context['weather_obj'] = fetch_real_time_weather()
    except:
        context['weather_obj'] = None
    
    # 2. Sales Data (Today)
    today = timezone.now().date()
    sales_today = DailySales.objects.filter(date=today).first()
    context['prediction_display'] = sales_today.revenue if sales_today else 0
    
    # 3. Inventory Context
    inv_count = Inventory.objects.filter(current_stock__lt=10).count()
    context['inventory_ctx'] = f"부족 품목 {inv_count}개" if inv_count > 0 else "재고 상태 양호"

    return render(request, 'platform_ui/dashboard.html', context)

def analytics_sales(request):
    """Detailed Sales Analysis"""
    return render(request, 'platform_ui/analytics_sales.html')

def analytics_forecast(request):
    """AI Sales Forecast"""
    return render(request, 'platform_ui/analytics_forecast.html')

def analytics_menu(request):
    """Menu Performance"""
    return render(request, 'platform_ui/analytics_menu.html')

def analytics_time(request):
    """Time/Day Insights"""
    return render(request, 'platform_ui/analytics_time.html')

def analytics_delivery(request):
    """Delivery Analysis"""
    return render(request, 'platform_ui/analytics_delivery.html')

def notifications_view(request):
    """Notification Center"""
    return render(request, 'platform_ui/notifications.html')

def settings_view(request):
    """Settings Page"""
    return render(request, 'platform_ui/settings.html')
