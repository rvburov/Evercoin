# evercoin/backend/api/wallets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WalletViewSet, WalletTransferViewSet, WalletConstantsViewSet

router = DefaultRouter()
router.register(
    r'wallets',
    WalletViewSet,
    basename='wallet'
)
router.register(
    r'transfers',
    WalletTransferViewSet,
    basename='wallet-transfer'
)
router.register(
    r'constants',
    WalletConstantsViewSet,
    basename='wallet-constants'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'wallets/summary/',
        WalletViewSet.as_view({'get': 'summary'}),
        name='wallet-summary'
    ),
]
