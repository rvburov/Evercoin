from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация через JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Управление пользователями (REST API)
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/add/', views.AccountAddView.as_view(), name='account_register'),
    path('account/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('account/delete/', views.AccountDeleteView.as_view(), name='account_delete'),

]
