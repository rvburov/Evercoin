# evercoin/backend/api/filters/apps.py
import django_filters
from .models import Wallet


class WalletFilter(django_filters.FilterSet):
    """
    Фильтры для счетов
    """
    
    balance_min = django_filters.NumberFilter(
        field_name='balance', 
        lookup_expr='gte',
        label='Минимальный баланс'
    )
    
    balance_max = django_filters.NumberFilter(
        field_name='balance', 
        lookup_expr='lte',
        label='Максимальный баланс'
    )
    
    currency = django_filters.ChoiceFilter(
        choices=Wallet._meta.get_field('currency').choices,
        label='Валюта'
    )
    
    is_default = django_filters.BooleanFilter(
        field_name='is_default',
        label='Счет по умолчанию'
    )
    
    is_hidden = django_filters.BooleanFilter(
        field_name='is_hidden',
        label='Скрытый счет'
    )
    
    created_after = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Создан после'
    )
    
    created_before = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Создан до'
    )
    
    class Meta:
        model = Wallet
        fields = [
            'currency',
            'is_default',
            'is_hidden',
            'balance_min',
            'balance_max',
            'created_after',
            'created_before'
        ]