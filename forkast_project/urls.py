from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.platform_ui import views as platform_views
from .api import api

urlpatterns = [
    path('admin/sales-forecast/', platform_views.sales_forecast_view, name='sales_forecast'),
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', include('apps.platform_ui.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
