from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация и регистрация (Логин и пароль)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # Аутентификация и регистрация (Провайдеров)
    path('auth/social/', include('dj_rest_auth.social.urls')), 
    path('auth/social/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('auth/social/yandex/', views.YandexLogin.as_view(), name='yandex_login'),

    # Управление пользователями (REST API)
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('account/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
]
