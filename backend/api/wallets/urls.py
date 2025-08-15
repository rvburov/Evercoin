# project/backend/api/notifications/urls.py
from django.urls import path
from .views import (
    WalletListCreateView,
    WalletDetailView,
    transfer_funds
)

urlpatterns = [
    path('wallets/', WalletListCreateView.as_view(), name='wallet-list'),
    path('wallets/<int:pk>/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallets/transfer/', transfer_funds, name='wallet-transfer'),
]
