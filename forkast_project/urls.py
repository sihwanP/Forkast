from django.contrib import admin
from django.urls import path, include
from apps.platform_ui import views as platform_views
from .api import api

urlpatterns = [
    path('admin/sales-forecast/', platform_views.sales_forecast_view, name='sales_forecast'),
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', include('apps.platform_ui.urls')),
]
