from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from config.api_keys import APIKeyTestView

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('users.urls')),
    
    # Защищённый API-эндпоинт с ключом
    path('config/', APIKeyTestView.as_view(), name='secure-api'),
    
    # Документация API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
