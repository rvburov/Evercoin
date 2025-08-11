from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/', include('dj_rest_auth.social.urls')), 

    # Управление пользователями (REST API)
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/register/', views.AccountRegisterView.as_view(), name='account_register'),
    path('account/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('account/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
]
