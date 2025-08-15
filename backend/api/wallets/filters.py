# project/backend/api/notifications/filters.py
import django_filters
from .models import Wallet

class WalletFilter(django_filters.FilterSet):
    """Фильтры для списка счетов"""
    min_balance = django_filters.NumberFilter(
        field_name='balance',
        lookup_expr='gte',
        label='Минимальный баланс'
    )
    max_balance = django_filters.NumberFilter(
        field_name='balance',
        lookup_expr='lte',
        label='Максимальный баланс'
    )
    currency = django_filters.CharFilter(
        field_name='currency',
        lookup_expr='iexact'
    )
    is_default = django_filters.BooleanFilter(
        field_name='is_default'
    )

    class Meta:
        model = Wallet
        fields = ['currency', 'is_default', 'exclude_from_total']
