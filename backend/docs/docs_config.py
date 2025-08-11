from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import path

urlpatterns = [
    # Генерирует схему OpenAPI (YAML/JSON)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI (интерактивная документация)
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    
    # Redoc (альтернативный просмотрщик)
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
