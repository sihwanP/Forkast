import os
import sys
import django
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime
from pathlib import Path

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forkast_project.settings')

# Oracle Driver Shim for Django
try:
    import oracledb
    import sys
    from datetime import datetime, date
    oracledb.version = "8.3.0"
    sys.modules["cx_Oracle"] = oracledb
    if not isinstance(oracledb.Binary, type):
        oracledb.Binary = bytes
    if not isinstance(oracledb.Timestamp, type):
        oracledb.Timestamp = datetime
    if not isinstance(oracledb.Date, type):
        oracledb.Date = date
except ImportError:
    pass

django.setup()

# We now import models to fetch real data
from platform_ui.models import DailySales, Inventory, Member, Order, Delivery, Transaction, Partner, Weather
from django.db.models import Sum, Max

def export():
    output_dir = Path("dothome_export")
    output_dir.mkdir(exist_ok=True)
    
    # Real Data from DB
    today = timezone.now().date()
    
    members = Member.objects.all().order_by('-created_at')
    inventory = Inventory.objects.all()
    orders = Order.objects.all().order_by('-created_at')
    deliveries = Delivery.objects.all().order_by('-scheduled_at')
    
    # Branch Stats Logic (Same as views.py)
    branch_stats = []
    for member in members:
        sales_agg = DailySales.objects.filter(item_name__icontains=member.name).aggregate(
            total_rev=Sum('revenue'),
            last_date=Max('date')
        )
        branch_stats.append({
            'id': member.id,
            'name': member.name,
            'total_revenue': int(sales_agg['total_rev'] or 0),
            'last_sale': sales_agg['last_date'],
            'is_approved': member.is_approved,
            'master_key': member.master_key
        })

    # KPI / Financials
    total_sales = Transaction.objects.filter(type='SALE', status='CONFIRMED').aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    pending_payments = Partner.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    low_stock_count = Inventory.objects.filter(status='LOW').count()
    pending_orders_count = Order.objects.filter(status='PENDING', type='SALES').count()

    # Weekly Chart (Real Aggregate)
    from datetime import timedelta
    start_week = today - timedelta(days=6)
    weekly_qs = DailySales.objects.filter(date__gte=start_week, date__lte=today).values('date').annotate(total_rev=Sum('revenue')).order_by('date')
    
    weekly_labels = []
    weekly_data = []
    day_names = ["월", "화", "수", "목", "금", "토", "일"]
    week_map = { (start_week + timedelta(days=i)): 0 for i in range(7) }
    for entry in weekly_qs:
        week_map[entry['date']] = int(entry['total_rev'])
    for d, rev in sorted(week_map.items()):
        weekly_labels.append(day_names[d.weekday()])
        weekly_data.append(rev)

    # Fake Request for Context Processors
    class FakeUser:
        is_authenticated = True
        is_staff = True
        is_superuser = True

    class FakeRequest:
        def __init__(self, path):
            self.path = path
            self.user = FakeUser()
            self.session = {'is_working': True, 'is_super_admin': True, 'super_admin_user': 'master'}
            self.resolver_match = type('Match', (), {'url_name': 'super_admin'})()
            self.GET = {}

    # 1. Super Admin Page (Index)
    print("Exporting Super Admin (Index)...")
    
    context = {
        'members': members,
        'branch_stats': branch_stats,
        'inventory': inventory,
        'orders': orders,
        'deliveries': deliveries,
        'total_sales': int(total_sales),
        'pending_payments': int(pending_payments),
        'low_stock_count': low_stock_count,
        'pending_orders_count': pending_orders_count,
        'admin_user': 'master',
        'weekly_chart': {
            'labels': weekly_labels,
            'data': weekly_data
        },
        'request': FakeRequest('/super-admin/')
    }
    
    # Fix Navigation Links (User Feedback: Branch->Admin, Site->Dashboard)
    def fix_nav_links(html_content):
        # 1. Site (사이트) -> Dashboard
        html_content = html_content.replace('href="/admin/"', 'href="./dashboard.html"')
        html_content = html_content.replace('href="./index.html"', 'href="./dashboard.html"') # If already relative
        
        # 2. Branch (지점) -> Index (Admin)
        html_content = html_content.replace('href="/dashboard/"', 'href="./index.html"')
        html_content = html_content.replace('href="./dashboard.html"', 'href="./index.html"')
        
        # 3. HQ (본사) -> Index
        html_content = html_content.replace('href="/super-admin/"', 'href="./index.html"')
        
        # 4. Restore correct mappings if any collision occurred above (Targeted Fixes)
        # We need to make sure the specific switch labels map correctly.
        # This is tricky with simple replaces. Let's use a more targeted approach for the switch specifically.
        
        # Reset just in case to a placeholder
        # (Assuming the html structure from templates)
        
        # SITE BUTTON Fix
        if '<span>사이트</span>' in html_content:
            # Find the anchor before '<span>사이트</span>'
            # We'll just hard replace specific known patterns
            
            # Pattern 1: admin/base_site.html output
            html_content = html_content.replace('href="/admin/" class="erp-switch-link', 'href="./dashboard.html" class="erp-switch-link')
            html_content = html_content.replace('href="/admin/" class="erp-switch-link active"', 'href="./dashboard.html" class="erp-switch-link active"')
            
            # Pattern 2: dashboard.html output (already relative)
            # It might have href="./index.html" currently for Site.
            # We want Site -> Dashboard.
            # But wait, looking at my view_file of dashboard.html, Site has href="./index.html".
            # I want to change THAT to ./dashboard.html
            pass

        return html_content

    # Apply fixes
    try:
        html = render_to_string('platform_ui/super_admin.html', context)
        html = html.replace('/static/', './static/')
        
        # Custom Link Logic
        # Global Replace first
        html = html.replace('href="/super-admin/"', 'href="./index.html"')
        
        # Targeted Switch replacement
        # Site -> Dashboard
        html = html.replace('href="/admin/" class="erp-switch-link', 'href="./dashboard.html" class="erp-switch-link')
        html = html.replace('href="/admin/"', 'href="./dashboard.html"') # General backup
        
        # Branch -> Admin (Index)
        html = html.replace('href="/dashboard/" class="erp-switch-link', 'href="./index.html" class="erp-switch-link')
        html = html.replace('href="/dashboard/"', 'href="./index.html"') # General backup

        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"Error rendering super_admin: {e}")


    # 2. Dashboard (Branch) Page
    print("Exporting Branch Dashboard...")
    
    # Real Dashboard Context (Same as views.py)
    # 1. Weather
    real_cond, real_temp = "맑음", 24 # Fallback or use DB
    weather_db = Weather.objects.filter(date=today).first()
    if weather_db:
        real_cond, real_temp = weather_db.condition, weather_db.temperature

    # 2. Sales Today
    sales_today_agg = DailySales.objects.filter(date=today).aggregate(total_revenue=Sum('revenue'))
    today_revenue = int(sales_today_agg['total_revenue'] or 0)
    
    # AI prediction (Use last stored or avg)
    predicted_rev = 1000000 
    
    # Inventory Simple Ctx
    inventory_items = Inventory.objects.all()
    inventory_ctx_str = ", ".join([f"{i.item_name}: {i.current_stock}" for i in inventory_items[:3]]) + "..."

    # Fake Request class for Context Processors
    class FakeUser:
        is_authenticated = True
        is_staff = True
        is_superuser = True

    class FakeRequest:
        def __init__(self, path):
            self.path = path
            self.user = FakeUser()
            self.session = {'is_working': True, 'is_super_admin': True, 'super_admin_user': 'master'}
            self.resolver_match = type('Match', (), {'url_name': 'dashboard'})()
            self.GET = {}

    context_dash = {
        'sales_today': type('Obj', (), {'revenue': today_revenue, 'orders': 0, 'predicted_revenue': predicted_rev}),
        'weather_obj': type('Obj', (), {'condition': real_cond, 'temperature': real_temp}),
        'inventory_ctx': inventory_ctx_str,
        'latest_sentiment': type('Obj', (), {'score': 95, 'summary': "긍정적인 하루입니다."}),
        'recent_posts': [],
        'is_working': True,
        'ai_loading': False, 
        'request': FakeRequest('/dashboard/')
    }
    context_dash['request'].resolver_match.url_name = 'dashboard'
    
    # Regex to find anchor tags in the switch (Tailwind version)
    # Structure: <a href="..." ...> ... <span>Text</span> ... </a>
    import re
    
    # We need separate replacers for Index and Dashboard because the "Active" state differs.
    
    # We need separate replacers for Index and Dashboard because the "Active" state differs.
    
    # For INDEX.html (Admin Page) -> User wants "Branch" (지점) to be Active/Current Page.
    def replacer_index(match):
        full_tag = match.group(0)
        href = match.group(1)
        text = match.group(2)
        
        # Link Logic
        new_href = href
        if '사이트' in text: new_href = './dashboard.html'
        elif '지점' in text or '가맹점' in text: new_href = './index.html' # Self
        elif '본사' in text: new_href = './index.html'
        
        # Active State Logic (For Index/Admin, Branch is Active)
        if '지점' in text or '가맹점' in text:
            # Activate: Remove slate-400, Add white.
            # We just force replace text-slate-400 -> text-white
            if 'text-slate-400' in full_tag:
                 full_tag = full_tag.replace('text-slate-400', 'text-white')
            # Ensure erp-switch-link gets active class if it exists (it might not in Tailwind version but good to share logic)
            if 'erp-switch-link' in full_tag and 'active' not in full_tag:
                 full_tag = full_tag.replace('erp-switch-link', 'erp-switch-link active')
                 
        elif '사이트' in text or '본사' in text:
            # Deactivate: Remove white, Add slate-400 (if white was there as primary color)
            # Be careful not to kill hover:text-white
            # Regex replace " text-white" (space before) to " text-slate-400"
            if ' text-white' in full_tag: 
                full_tag = full_tag.replace(' text-white', ' text-slate-400')
            if 'active' in full_tag: 
                full_tag = full_tag.replace('active', '')
            
        # Update Href
        full_tag = full_tag.replace(href, new_href)
        return full_tag

    # For DASHBOARD.html -> User wants "Site" (사이트) to be Active/Current Page.
    def replacer_dashboard(match):
        full_tag = match.group(0)
        href = match.group(1)
        text = match.group(2)
        
        # Link Logic
        new_href = href
        if '사이트' in text: new_href = './dashboard.html' # Self
        elif '지점' in text or '가맹점' in text: new_href = './index.html'
        elif '본사' in text: new_href = './index.html'

        # Active State Logic (For Dashboard, Site is Active)
        if '사이트' in text:
            # Activate
            if 'text-slate-400' in full_tag:
                 full_tag = full_tag.replace('text-slate-400', 'text-white')
            if 'erp-switch-link' in full_tag and 'active' not in full_tag:
                 full_tag = full_tag.replace('erp-switch-link', 'erp-switch-link active')

        elif '지점' in text or '본사' in text or '가맹점' in text:
            # Deactivate
            if ' text-white' in full_tag: 
                full_tag = full_tag.replace(' text-white', ' text-slate-400')
            if 'active' in full_tag: 
                full_tag = full_tag.replace('active', '')
            
        # Update Href
        full_tag = full_tag.replace(href, new_href)
        return full_tag

    # Helper for Background Slider Position Fix (CSS)
    def fix_slider_pos(html, active_target):
        # active_target: 'site' (center/33%) or 'branch' (right/66%)
        # Default in templates might be wrong.
        if active_target == 'site':
            # Center
            return re.sub(r'left:\s*[^;]+;', 'left: 33.33%;', html)
        elif active_target == 'branch':
            # Right
            return re.sub(r'left:\s*[^;]+;', 'left: 66.66%;', html)
        return html

    pattern = re.compile(r'<a href="([^"]+)"[^>]*>.*?<span>(.*?)</span>.*?</a>', re.DOTALL)

    try:
        # 1. Super Admin -> index.html (TARGET: BRANCH Active)
        print("Exporting Super Admin (Index)...")
        html = render_to_string('platform_ui/super_admin.html', context)
        html = html.replace('/static/', './static/')
        
        # Base replacements
        html = html.replace('href="/super-admin/"', 'href="./index.html"')
        html = html.replace('href="/admin/"', 'href="./index.html"') 
        html = html.replace('href="/dashboard/"', 'href="./dashboard.html"')
        
        # Fix Switch Links & Active State
        html = re.sub(pattern, replacer_index, html)
        
        # Fix Slider Position for Admin (Branch is Right/3rd?)
        # Base site has 3 items: HQ, Site, Branch.
        # User wants Branch to be Admin. So Slider should be on Branch (Right).
        # Admin base_site.html usually puts it on Site (Center).
        # We need to find the style="...left:..." block.
        # It's usually inline style or CSS class.
        # The CSS in base_site.html has: .erp-switch-bg { left: calc(33.33% + 2px); }
        # We need to change that to ~66% for Branch.
        html = html.replace('left: calc(33.33% + 2px);', 'left: calc(66.66% - 4px);')
        
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # 2. Dashboard -> dashboard.html (TARGET: SITE Active)
        print("Exporting Dashboard...")
        context_dash['request'].resolver_match.url_name = 'dashboard'
        html_dash = render_to_string('platform_ui/dashboard.html', context_dash)
        html_dash = html_dash.replace('/static/', './static/')
        
        # Base replacements
        html_dash = html_dash.replace('href="/super-admin/"', 'href="./index.html"')
        html_dash = html_dash.replace('href="/admin/"', 'href="./index.html"') 
        html_dash = html_dash.replace('href="/toggle_work/"', 'href="#"') 
        html_dash = html_dash.replace('href="/dashboard/"', 'href="./dashboard.html"')

        # Fix Switch Links & Active State
        html_dash = re.sub(pattern, replacer_dashboard, html_dash)
        
        # Fix Slider Position for Dashboard (Site is Center/2nd?)
        # Dashboard template usually puts it on Branch (Right/66%).
        # We want Site (Center/33%).
        # Loop for `style="...left:..."` on the bg div
        html_dash = re.sub(r'left:\s*calc\(66.66%\);', 'left: 33.33%;', html_dash)
        html_dash = re.sub(r'left:\s*66.66%;', 'left: 33.33%;', html_dash)
        
        mock_api_data = """
        Promise.resolve({
            status: 'success',
            prediction: 1350000,
            weather: { condition: '맑음', temp: 24 },
            analysis: "최근 매출 흐름이 매우 좋습니다. 점심 피크 인력 충원과 재고 점검을 추천합니다.",
            strategies: [
                {
                    icon: '🚀', title: '긴급 타임 세일', summary: '오후 2시~4시 15% 할인', score: 92,
                    detail: '유동 인구가 많은 시간대에 할인을 적용하여 방문율을 극대화하세요.'
                },
                {
                    icon: '📦', title: '재고 최적화', summary: '인기 품목 선제적 발주', score: 85,
                    detail: '주말 대비 수요가 높을 것으로 예상되는 원두와 우유를 추가 확보하세요.'
                },
                {
                    icon: '👥', title: '인력 효율화', summary: '피크타임 파트타임 배치', score: 88,
                    detail: '매출 집중 시간대에 인력을 재배치하여 서비스 품질을 유지하세요.'
                }
            ],
            hourly_sales: [0,0,0,0,0,0,0,150000,320000,450000,680000,950000,420000,300000,0,0,0,0,0,0,0,0,0,0],
            past_hourly_sales: [0,0,0,0,0,0,0,120000,280000,410000,600000,850000,380000,290000,0,0,0,0,0,0,0,0,0,0]
        })
        """
        
        # [NEW] Mock API Call for Static Export (Regex for extreme robustness)
        # 1. Match any fetch that look like a django url or our api path
        fetch_regex = r'fetch\s*\(\s*(["\'])(.*?dashboard_stats_api.*?|.*?\/api\/dashboard-stats\/.*?)\1\s*\)'
        
        if re.search(fetch_regex, html_dash):
            print("Found fetch call in dashboard.html, injecting mock data...")
            html_dash = re.sub(fetch_regex, mock_api_data, html_dash)
            
            # Match .then(r=>r.json()) regardless of whitespace/newlines
            then_regex = r'\.then\s*\(\s*r\s*=>\s*r\.json\(\)\s*\)'
            html_dash = re.sub(then_regex, '', html_dash)
        else:
            print("WARNING: Could not find fetch call to /api/dashboard-stats/ in dashboard.html")
            # Alternative: replace the whole Init Logic block if needed, but regex is usually better
        
        with open(output_dir / "dashboard.html", "w", encoding="utf-8") as f:
            f.write(html_dash)

    except Exception as e:
        import traceback
        print(f"Error rendering export: {e}")
        traceback.print_exc()

    print(f"Export Complete! Files are in {output_dir.absolute()}")
    print("Please copy the 'static' folder into 'dothome_export' as well.")

if __name__ == "__main__":
    export()
