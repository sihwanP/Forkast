from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.cover, name='cover'),
    # Main Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Analytics Routes
    path('analytics/sales/', views.analytics_sales, name='analytics_sales'),
    path('analytics/forecast/', views.analytics_forecast, name='analytics_forecast'),
    path('analytics/menu/', views.analytics_menu, name='analytics_menu'),
    path('analytics/time/', views.analytics_time, name='analytics_time'),
    path('analytics/delivery/', views.analytics_delivery, name='analytics_delivery'),
    
    # Management Routes
    path('notifications/', views.notifications_view, name='notifications'),
    path('settings/', views.settings_view, name='settings'),

    # API & Legacy
    path('toggle_work/', views.toggle_work_status, name='toggle_work'),
    path('verify-admin/', views.verify_admin, name='verify_admin'),
    path('change-admin-key/', views.change_admin_key, name='change_admin_key'),
    path('reset-admin-key/', views.reset_admin_key, name='reset_admin_key'),
    path('super-admin/', views.super_admin, name='super_admin'),
    path('super-admin/logout/', views.super_admin_logout, name='super_admin_logout'),
    path('api/dashboard-stats/', views.dashboard_stats_api_v2, name='dashboard_stats_api'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/api/', views.inventory_api, name='inventory_api'),
    path('inventory/order/', views.order_api, name='order_api'),
    path('sales/', views.sales_view, name='sales_dashboard'), 
    path('api/analytics/sales-stats/', views.sales_period_stats_api, name='sales_period_stats_api'),
    path('api/upload-csv/', views.upload_csv_api, name='upload_csv_api'),
    path('api/upload-past-csv/', views.upload_past_csv_api, name='upload_past_csv_api'),
    path('favicon.ico', TemplateView.as_view(template_name="platform_ui/favicon_dummy.html", content_type='image/png')),
    
    path('serviceworker.js', TemplateView.as_view(template_name="serviceworker.js", content_type='application/javascript')),
]
