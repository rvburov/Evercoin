from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # Пользователь
    path('api/users/', include('users.urls')),
    
    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
