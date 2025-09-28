# evercoin/backend/api/wallets/urls.py
from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    # Список счетов
    path('wallets/', views.WalletListView.as_view(), name='wallet-list'),
    
    # Детали счета
    path('wallets/<int:pk>/', views.WalletDetailView.as_view(), name='wallet-detail'),
    
    # Создание счета
    path('wallets/create/', views.WalletCreateView.as_view(), name='wallet-create'),
    
    # Обновление счета
    path('wallets/<int:pk>/update/', views.WalletUpdateView.as_view(), name='wallet-update'),
    
    # Удаление счета
    path('wallets/<int:pk>/delete/', views.WalletDeleteView.as_view(), name='wallet-delete'),
    
    # Перевод между счетами
    path('wallets/transfer/', views.WalletTransferView.as_view(), name='wallet-transfer'),
    
    # Общий баланс
    path('wallets/balance/', views.WalletBalanceView.as_view(), name='wallet-balance'),
    
    # Установка счета по умолчанию
    path('wallets/<int:pk>/set-default/', views.WalletSetDefaultView.as_view(), name='wallet-set-default'),
    
    # История баланса счета
    path('wallets/<int:pk>/history/', views.WalletHistoryView.as_view(), name='wallet-history'),
    
    # Статистика по счетам
    path('wallets/statistics/', views.wallet_statistics, name='wallet-statistics'),
]
