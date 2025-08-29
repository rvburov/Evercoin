# evercoin/backend/api/users/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from . import views

# Роутер для API views
router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    
    # Аутентификация
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Управление паролями
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Управление аккаунтом
    path('account/', views.AccountDetailView.as_view(), name='account_detail'),
    path('account/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('account/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
]
