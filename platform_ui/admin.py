from django.contrib import admin
from .models import DailySales, Inventory, Weather, LocalEvent, OwnerSentiment, CommunityPost, Consultation, Member, AdminConfig, Order

# Register all models with better visibility
@admin.register(DailySales)
class DailySalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'item_name', 'revenue', 'predicted_revenue')
    list_filter = ('date', 'item_name')
    search_fields = ('item_name',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'current_stock', 'optimal_stock', 'status')
    list_filter = ('status',)
    search_fields = ('item_name',)

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ('date', 'condition', 'temperature')

@admin.register(LocalEvent)
class LocalEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'impact_level')

@admin.register(OwnerSentiment)
class OwnerSentimentAdmin(admin.ModelAdmin):
    list_display = ('date', 'mood_score', 'cheer_message')

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'master_key', 'created_at')

@admin.register(AdminConfig)
class AdminConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'status', 'created_at')
    list_filter = ('status',)

# Admin Site Customization
admin.site.site_header = "포카스트 AI (Forkast AI) 관리 시스템"
admin.site.site_title = "Forkast Admin"
admin.site.index_title = "데이터 제어 및 AI 분석 관리"
