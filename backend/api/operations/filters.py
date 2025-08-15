# project/backend/api/operations/filters.py
import django_filters
from .models import Operation
from django.utils import timezone
from datetime import timedelta

class OperationFilter(django_filters.FilterSet):
    """Фильтры для операций с поддержкой периодов"""
    date_range = django_filters.CharFilter(method='filter_by_date_range')
    operation_type = django_filters.CharFilter(field_name='operation_type')
    category = django_filters.NumberFilter(field_name='category_id')
    wallet = django_filters.NumberFilter(field_name='wallet_id')

    class Meta:
        model = Operation
        fields = ['operation_type', 'category', 'wallet']

    def filter_by_date_range(self, queryset, name, value):
        """Фильтрация по временным периодам (day/week/month/year)"""
        now = timezone.now()
        if value == 'day':
            return queryset.filter(date__date=now.date())
        elif value == 'week':
            start = now - timedelta(days=now.weekday())
            return queryset.filter(date__gte=start.date())
        elif value == 'month':
            return queryset.filter(date__month=now.month, date__year=now.year)
        elif value == 'year':
            return queryset.filter(date__year=now.year)
        return queryset
