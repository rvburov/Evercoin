# evercoin/backend/api/operations/filters.py
import django_filters
from django.db import models
from .models import Operation


class OperationFilter(django_filters.FilterSet):
    """
    Фильтры для операций
    """
    
    date_from = django_filters.DateFilter(
        field_name='operation_date', 
        lookup_expr='gte',
        label='Дата от'
    )
    
    date_to = django_filters.DateFilter(
        field_name='operation_date', 
        lookup_expr='lte',
        label='Дата до'
    )
    
    amount_min = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='gte',
        label='Минимальная сумма'
    )
    
    amount_max = django_filters.NumberFilter(
        field_name='amount', 
        lookup_expr='lte',
        label='Максимальная сумма'
    )
    
    wallet = django_filters.NumberFilter(
        field_name='wallet__id',
        label='ID счета'
    )
    
    category = django_filters.NumberFilter(
        field_name='category__id',
        label='ID категории'
    )
    
    operation_type = django_filters.ChoiceFilter(
        choices=Operation.OPERATION_TYPES,
        label='Тип операции'
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='Поиск по названию и описанию'
    )
    
    class Meta:
        model = Operation
        fields = [
            'operation_type',
            'wallet',
            'category',
            'date_from',
            'date_to',
            'amount_min',
            'amount_max',
            'search'
        ]
    
    def filter_search(self, queryset, name, value):
        """
        Поиск по названию и описанию операции
        """
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value)
        )
