# evercoin/backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Административная панель
    path('api/admin/', admin.site.urls),
    
    # Пользователь
    path('api/users/', include('api.users.urls')),

    # Операции
    path('api/operations/', include('api.operations.urls')),

    # Счета
    path('api/wallets/', include('api.wallets.urls')),
    
    # Категории
    path('api/categories/', include('api.categories.urls')),
    
    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
