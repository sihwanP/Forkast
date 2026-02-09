from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import (
    Inventory, TaxCode, Partner, Transaction, TransactionItem, InventoryMovement,
    PosRawSales, PosItemMap, DailySales, ForecastRun, Member, AdminConfig, AuditLog,
    Order, Weather, LocalEvent, OwnerSentiment, CommunityPost, Consultation, Delivery,
    SalesOrder, PurchaseOrder, Inbound, Outbound
)

# ==========================================
# Common Actions & Helpers
# ==========================================

def export_to_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_to_csv.short_description = "선택된 항목 엑셀(CSV) 다운로드"

class BaseErpAdmin(admin.ModelAdmin):
    actions = [export_to_csv]
    list_per_page = 20

# ==========================================
# 1. CORE MASTER DATA
# ==========================================

@admin.register(Inventory)
class ProductAdmin(BaseErpAdmin):
    # High Quality ERP: Product & Inventory Management
    list_display = ('item_name', 'image_thumbnail', 'category', 'stock_progress', 'price_info', 'value_display', 'status_badge')
    list_filter = ('category', 'status', 'tax_code')
    search_fields = ('item_name', 'code')
    change_list_template = 'admin/inventory_change_list.html'

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">', obj.image.url)
        return format_html('<span style="color: #cbd5e1; font-size: 20px;"><i class="fa-solid fa-box"></i></span>')
    image_thumbnail.short_description = "이미지"

    def stock_progress(self, obj):
        # Visual Stock Bar
        percent = 0
        if obj.optimal_stock > 0:
            percent = min(100, int((obj.current_stock / obj.optimal_stock) * 100))
        
        color = "#10b981" # Green
        if percent < 30: color = "#ef4444" # Red
        elif percent > 100: color = "#f59e0b" # Orange
        
        return format_html(
            '''
            <div style="width: 100px; background-color: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;">
                <div style="width: {}%; background-color: {}; height: 100%;"></div>
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
                {} / {} ({}%)
            </div>
            ''',
            percent, color, obj.current_stock, obj.optimal_stock, percent
        )
    stock_progress.short_description = "재고 현황"

    def price_info(self, obj):
        # Calculation of Margin
        margin = 0
        if obj.price > 0:
            margin = int(((obj.price - obj.cost) / obj.price) * 100)
        
        return format_html(
            '''
            <div>
                <span style="font-weight:bold;">₩{}</span>
                <div style="font-size: 11px; color: #64748b;">
                    Cost: ₩{} <span style="color: #10b981;">(Mg: {}%)</span>
                </div>
            </div>
            ''',
            format(obj.price, ","), format(obj.cost, ","), margin
        )
    price_info.short_description = "가격 및 마진"

    def value_display(self, obj):
        total_val = obj.current_stock * obj.cost
        return format_html('<span style="font-family:monospace; font-weight:bold;">₩{}</span>', format(total_val, ","))
    value_display.short_description = "재고 자산 가치"

    def status_badge(self, obj):
        colors = {'GOOD': '#10b981', 'LOW': '#ef4444', 'OVER': '#f59e0b'}
        labels = {'GOOD': '적정', 'LOW': '부족', 'OVER': '과잉'}
        return format_html(
            '<span style="color:{}; background-color:rgba(0,0,0,0.05); padding:4px 8px; border-radius:6px; font-weight:bold; border: 1px solid {};">{}</span>',
            colors.get(obj.status, 'gray'),
            colors.get(obj.status, 'gray'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = "상태"

    # Override changelist setup to calculate aggregate data for the dashboard
    def changelist_view(self, request, extra_context=None):
        # Aggregate logic
        from django.db.models import Sum, F
        total_items = Inventory.objects.count()
        total_value = Inventory.objects.aggregate(
            total_val=Sum(F('current_stock') * F('cost'))
        )['total_val'] or 0
        low_stock = Inventory.objects.filter(status='LOW').count()
        
        extra_context = extra_context or {}
        extra_context['erp_total_items'] = total_items
        extra_context['erp_total_value'] = total_value
        extra_context['erp_low_stock'] = low_stock
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Partner)
class PartnerAdmin(BaseErpAdmin):
    list_display = ('name', 'type', 'balance', 'balance_colored', 'contact_info_summary')
    list_filter = ('type',)
    search_fields = ('name', 'contact_info')
    list_editable = ('type', 'balance')

    def balance_colored(self, obj):
        color = "#10b981" if obj.balance >= 0 else "#ef4444"
        return format_html('<span style="color:{}; font-weight:bold;">₩{}</span>', color, format(obj.balance, ","))
    balance_colored.short_description = "잔액/미수금"

    def contact_info_summary(self, obj):
        return obj.contact_info[:30] + "..." if len(obj.contact_info) > 30 else obj.contact_info
    contact_info_summary.short_description = "비고/연락처"

@admin.register(TaxCode)
class TaxCodeAdmin(BaseErpAdmin):
    list_display = ('name', 'rate')

# ==========================================
# 2. TRANSACTIONS
# ==========================================

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1
    fields = ('product', 'product_name', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)

@admin.register(Transaction)
class TransactionAdmin(BaseErpAdmin):
    list_display = ('id', 'transaction_date', 'type_badge', 'partner', 'total_amount_display', 'status', 'status_colored')
    list_filter = ('type', 'status', 'transaction_date')
    search_fields = ('id', 'partner__name')
    date_hierarchy = 'transaction_date'
    inlines = [TransactionItemInline]
    list_editable = ('status',)

    def type_badge(self, obj):
        colors = {'SALE': '#3b82f6', 'PURCHASE': '#8b5cf6', 'REFUND': '#ef4444'}
        return format_html('<span style="background:{}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{}</span>', colors.get(obj.type, 'gray'), obj.get_type_display())
    type_badge.short_description = "유형"

    def total_amount_display(self, obj):
        return format_html('<span style="font-family:monospace; font-weight:bold;">₩{}</span>', format(obj.final_amount, ","))
    total_amount_display.short_description = "최종 합계"
    
    def status_colored(self, obj):
        colors = {'PENDING': 'orange', 'CONFIRMED': 'green', 'CANCELLED': 'red'}
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = "상태"

@admin.register(InventoryMovement)
class InventoryMovementAdmin(BaseErpAdmin):
    list_display = ('created_at', 'type_badge', 'product_name', 'quantity', 'reason')
    list_filter = ('type', 'created_at')
    search_fields = ('product__item_name', 'product_name', 'reason')
    date_hierarchy = 'created_at'
    change_list_template = 'admin/logistics_change_list.html'

    def type_badge(self, obj):
        color = '#10b981' if obj.type == 'IN' else '#ef4444'
        label = '입고' if obj.type == 'IN' else '출고'
        return format_html('<span style="background:{}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold; font-size:11px;">{}</span>', color, label)
    type_badge.short_description = "유형"

# ==========================================
# 3. POS & LOGS
# ==========================================

@admin.register(PosRawSales)
class PosRawSalesAdmin(BaseErpAdmin):
    list_display = ('received_at', 'status', 'view_payload_summary')
    list_filter = ('status', 'received_at')
    readonly_fields = ('received_at', 'payload', 'error_log')
    
    def view_payload_summary(self, obj):
        return str(obj.payload)[:50] + "..." if obj.payload else "-"
    view_payload_summary.short_description = "데이터 미리보기"

@admin.register(PosItemMap)
class PosItemMapAdmin(BaseErpAdmin):
    list_display = ('pos_code', 'product_name', 'internal_product')
    search_fields = ('pos_code', 'internal_product__item_name', 'product_name')

@admin.register(AuditLog)
class AuditLogAdmin(BaseErpAdmin):
    list_display = ('timestamp', 'user', 'action', 'target')
    list_filter = ('action', 'timestamp')
    search_fields = ('user', 'target', 'details')
    readonly_fields = ('timestamp', 'user', 'action', 'target', 'details')

# ==========================================
# 4. ANALYTICS & AI
# ==========================================

@admin.register(DailySales)
class DailySalesAdmin(BaseErpAdmin):
    list_display = ('date', 'item_name', 'revenue', 'predicted_revenue')
    list_filter = ('date', 'item_name')
    actions = [export_to_csv] # Explicitly add just in case

@admin.register(ForecastRun)
class ForecastRunAdmin(BaseErpAdmin):
    list_display = ('run_date', 'model_name', 'status', 'metrics_summary')
    readonly_fields = ('run_date', 'accuracy_metrics')

    def metrics_summary(self, obj):
        return str(obj.accuracy_metrics)

# ==========================================
# 5. LEGACY / SETTINGS
# ==========================================

@admin.register(Member)
class MemberAdmin(BaseErpAdmin):
    list_display = ('name', 'master_key', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('name',)

@admin.register(AdminConfig)
class AdminConfigAdmin(BaseErpAdmin):
    list_display = ('key', 'updated_at')

# ==========================================
# Helper: 재고 상태 자동 재계산
# ==========================================
def recalculate_inventory_status(product):
    """재고 비율에 따라 상태(LOW/GOOD/OVER) 자동 재계산."""
    if product.optimal_stock > 0:
        ratio = product.current_stock / product.optimal_stock
    else:
        ratio = 1.0
    if ratio < 0.3:
        product.status = 'LOW'
    elif ratio > 1.5:
        product.status = 'OVER'
    else:
        product.status = 'GOOD'
    product.save()

# ==========================================
# Custom Actions for Logistics
# ==========================================
def confirm_delivery_receipt(modeladmin, request, queryset):
    """입고 확인: 재고 증가 + 상태 자동 재계산."""
    from .models import InventoryMovement
    count = 0
    for order in queryset.filter(status='PENDING'):
        order.status = 'COMPLETED'
        order.save()
        # 재고 증가
        product = order.item
        product.current_stock += order.quantity
        product.save()
        recalculate_inventory_status(product)
        # 입출고 이력 기록
        InventoryMovement.objects.create(
            type='IN',
            product=order.item,
            quantity=order.quantity,
            reason=f'입고 확인 - 주문 #{order.id}'
        )
        count += 1
    modeladmin.message_user(request, f'{count}건의 입고가 확인되었습니다.')
confirm_delivery_receipt.short_description = "선택 항목 입고 확인"

def cancel_order(modeladmin, request, queryset):
    """주문 취소: 완료된 주문은 재고 원복 + 배송 취소 + 상태 재계산."""
    from .models import InventoryMovement, Delivery
    count = 0
    for order in queryset.exclude(status='CANCELLED'):
        if order.status == 'COMPLETED':
            # 재고 원복
            product = order.item
            if order.type == 'SALES':  # 출고였으므로 재고 복원
                product.current_stock += order.quantity
            else:  # 입고였으므로 재고 차감
                product.current_stock -= order.quantity
            product.save()
            recalculate_inventory_status(product)
            # 연관 배송 취소
            Delivery.objects.filter(order=order).exclude(status='CANCELLED').update(status='CANCELLED')
        order.status = 'CANCELLED'
        order.save()
        count += 1
    modeladmin.message_user(request, f'{count}건의 주문이 취소되었습니다.')
cancel_order.short_description = "선택 항목 주문 취소"

def approve_sales_order(modeladmin, request, queryset):
    """수주 승인: Delivery 자동 생성 + 재고 차감 + 이력 기록."""
    from .models import InventoryMovement, Delivery
    from django.utils import timezone
    count = 0
    for order in queryset.filter(status='PENDING'):
        order.status = 'COMPLETED'
        order.save()
        # 재고 차감 (출고)
        product = order.item
        product.current_stock -= order.quantity
        product.save()
        recalculate_inventory_status(product)
        # 배송 자동 생성
        Delivery.objects.get_or_create(
            order=order,
            defaults={
                'delivery_address': order.branch_name or '지점 배송',
                'status': 'SCHEDULED',
                'scheduled_at': timezone.now()
            }
        )
        # 입출고 이력 기록
        InventoryMovement.objects.create(
            type='OUT',
            product=order.item,
            quantity=order.quantity,
            reason=f'수주 승인 및 배송 예약 (Order #{order.id})'
        )
        count += 1
    modeladmin.message_user(request, f'{count}건의 수주가 승인되었습니다. 배송이 자동 생성되었습니다.')
approve_sales_order.short_description = "선택 수주 승인 (배송 자동 생성)"

@admin.register(Order)
class OrderAdmin(BaseErpAdmin):
    list_display = ('id', 'product_name', 'quantity', 'status_badge', 'created_at', 'delivery_link')
    list_editable = ('quantity',)
    list_filter = ('status', 'type')
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv, approve_sales_order, confirm_delivery_receipt, cancel_order]

    def status_badge(self, obj):
        colors = {'PENDING': '#f59e0b', 'COMPLETED': '#10b981', 'CANCELLED': '#ef4444'}
        labels = {'PENDING': '대기', 'COMPLETED': '완료', 'CANCELLED': '취소'}
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', colors.get(obj.status, 'black'), labels.get(obj.status, obj.status))
    status_badge.short_description = "상태"

    def delivery_link(self, obj):
        try:
            if obj.delivery:
                return format_html('<a href="../delivery/{}/change/?_popup=1" target="erp-detail-frame" style="color:#3b82f6; text-decoration:underline;">{}</a>', 
                                   obj.delivery.id, obj.delivery.get_status_display())
        except Delivery.DoesNotExist:
            pass
        return "N/A"
    delivery_link.short_description = "배송 정보"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pending_count'] = Order.objects.filter(status='PENDING').count()
        extra_context['transit_count'] = Order.objects.filter(status='COMPLETED').count()
        extra_context['completed_count'] = Order.objects.filter(status='COMPLETED').count()
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Delivery)
class DeliveryAdmin(BaseErpAdmin):
    list_display = ('id', 'order_info', 'status_timeline', 'driver_name', 'scheduled_at')
    list_filter = ('status', 'scheduled_at')
    search_fields = ('order__id', 'driver_name', 'vehicle_info')
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv]

    def order_info(self, obj):
        return format_html('<b>#{}</b><br><span style="font-size:11px; color:#64748b;">{}</span>', obj.order.id, obj.order.item.item_name)
    order_info.short_description = "주문 번호"

    def status_timeline(self, obj):
        steps = ['SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'RETURNED']
        current_idx = steps.index(obj.status) if obj.status in steps else -1
        
        html = '<div style="display:flex; gap:4px; align-items:center;">'
        for i, step in enumerate(['준비', '이동', '완료']):
            opacity = "1" if i <= current_idx else "0.2"
            color = "#3b82f6" if i <= current_idx else "#94a3b8"
            html += f'<div style="width:20px; height:4px; background:{color}; opacity:{opacity}; border-radius:2px;"></div>'
        html += f'<span style="font-size:11px; margin-left:8px; font-weight:bold; color:#1e293b;">{obj.get_status_display()}</span></div>'
        return format_html(html)
    status_timeline.short_description = "물류 타임라인"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pending_count'] = Delivery.objects.filter(status='SCHEDULED').count()
        extra_context['transit_count'] = Delivery.objects.filter(status='IN_TRANSIT').count()
        extra_context['completed_count'] = Delivery.objects.filter(status='DELIVERED').count()
        return super().changelist_view(request, extra_context=extra_context)

# Simple Registers
admin.site.register(Weather)
admin.site.register(LocalEvent)
admin.site.register(OwnerSentiment)
admin.site.register(CommunityPost)
admin.site.register(Consultation)

# Use existing customization
admin.site.site_header = "Forkast ERP 통합 관리"
admin.site.site_title = "Forkast Admin"
admin.site.index_title = "시스템 관리자 콘솔"

# ==========================================
# 6. DEDICATED LOGISTICS PAGES
# ==========================================

@admin.register(SalesOrder)
class SalesOrderAdmin(BaseErpAdmin):
    """
    수주 관리 (가맹점 주문) 전용 페이지
    """
    list_display = ('id', 'branch_name', 'product_name', 'quantity', 'status_badge', 'created_at', 'delivery_action')
    list_editable = ('quantity',)
    list_filter = ('status', 'branch_name')
    search_fields = ('branch_name', 'item__item_name', 'product_name')
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv, approve_sales_order, cancel_order]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='SALES')

    def status_badge(self, obj):
        colors = {'PENDING': '#f59e0b', 'COMPLETED': '#10b981', 'CANCELLED': '#ef4444'}
        labels = {'PENDING': '승인 대기', 'COMPLETED': '출고 완료', 'CANCELLED': '주문 취소'}
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>', 
            colors.get(obj.status, 'black'), labels.get(obj.status, obj.status)
        )
    status_badge.short_description = "진행 상태"

    def delivery_action(self, obj):
        try:
            if obj.status == 'COMPLETED' and obj.delivery:
                return format_html(
                    '<a href="/admin/platform_ui/outbound/{}/change/" style="color:#3b82f6;">배송 #{}</a>',
                    obj.delivery.id, obj.delivery.id
                )
        except Delivery.DoesNotExist:
            pass
        if obj.status == 'PENDING':
            return format_html('<span style="color:#f59e0b; font-weight:bold;">승인 대기 (체크 후 액션 사용)</span>')
        return "-"
    delivery_action.short_description = "배송 관리"

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(BaseErpAdmin):
    """
    발주 관리 (공급사 발주) 전용 페이지
    """
    list_display = ('id', 'product_name', 'quantity', 'status_badge', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('status',)
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv, confirm_delivery_receipt, cancel_order]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='PURCHASE')
    
    def status_badge(self, obj):
        colors = {'PENDING': '#f59e0b', 'COMPLETED': '#10b981', 'CANCELLED': '#ef4444'}
        labels = {'PENDING': '입고 대기', 'COMPLETED': '입고 완료', 'CANCELLED': '발주 취소'}
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            colors.get(obj.status, '#4338ca'), labels.get(obj.status, obj.get_status_display())
        )
    status_badge.short_description = "상태"

def cancel_inbound(modeladmin, request, queryset):
    """입고 취소: 재고 원복 + 상태 재계산."""
    count = 0
    for move in queryset:
        product = move.product
        product.current_stock -= move.quantity
        product.save()
        recalculate_inventory_status(product)
        move.delete()
        count += 1
    modeladmin.message_user(request, f'{count}건의 입고가 취소되었습니다. 재고가 원복되었습니다.')
cancel_inbound.short_description = "선택 입고 취소 (재고 원복)"

def cancel_delivery(modeladmin, request, queryset):
    """배송 취소."""
    count = queryset.exclude(status='CANCELLED').update(status='CANCELLED')
    modeladmin.message_user(request, f'{count}건의 배송이 취소되었습니다.')
cancel_delivery.short_description = "선택 배송 취소"

@admin.register(Inbound)
class InboundAdmin(BaseErpAdmin):
    """
    입고 관리 (본사 입고) 전용 페이지
    """
    list_display = ('created_at', 'product_name', 'quantity', 'reason', 'status_label')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    search_fields = ('product__item_name', 'product_name')
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv, cancel_inbound]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type='IN')

    def status_label(self, obj):
        return format_html('<span style="color:#16a34a; font-weight:bold;">입고 완료</span>')
    status_label.short_description = "상태"

@admin.register(Outbound)
class OutboundAdmin(BaseErpAdmin):
    """
    출고 관리 (배송 현황) 전용 페이지
    """
    list_display = ('id', 'order_ref', 'driver_name', 'status_timeline', 'scheduled_at')
    list_filter = ('status',)
    search_fields = ('order__item__item_name', 'driver_name')
    change_list_template = 'admin/logistics_master_detail.html'
    actions = [export_to_csv, cancel_delivery]

    def order_ref(self, obj):
        return format_html('<b>Order #{}</b><br>{}', obj.order.id, obj.order.item.item_name)
    order_ref.short_description = "연관 주문"

    def status_timeline(self, obj):
        # Visual timeline
        steps = ['SCHEDULED', 'IN_TRANSIT', 'DELIVERED']
        current_idx = steps.index(obj.status) if obj.status in steps else -1
        
        html = '<div style="display:flex; gap:4px; align-items:center;">'
        labels = ['준비', '이동', '완료']
        for i, label in enumerate(labels):
            is_active = i <= current_idx
            color = "#2563eb" if is_active else "#cbd5e1"
            opacity = "1" if is_active else "0.5"
            html += f'<div style="width:30px; height:4px; background:{color}; opacity:{opacity}; border-radius:2px;" title="{label}"></div>'
        
        badge_color = "#2563eb" if obj.status == 'DELIVERED' else "#475569"
        html += f'<span style="font-size:11px; margin-left:8px; font-weight:bold; color:{badge_color};">{obj.get_status_display()}</span></div>'
        return format_html(html)
    status_timeline.short_description = "배송 진행률"
