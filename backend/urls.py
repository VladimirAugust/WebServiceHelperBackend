from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('common/', include('common.urls')),
    path('api/', include('account.urls')),
    path('api/trade/', include('trade.urls')),
]

admin.site.site_header = "Общество взаимообмена"

if settings.DEVELOPMENT:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
