# evercoin/backend/api/analytics/filters.py
import django_filters
from .models import CachedAnalytics, ReportPreset


class CachedAnalyticsFilter(django_filters.FilterSet):
    """
    Фильтры для кешированной аналитики
    """
    
    cache_type = django_filters.ChoiceFilter(
        choices=CachedAnalytics.CACHE_TYPES,
        label='Тип кеша'
    )
    
    period_start = django_filters.DateFilter(
        field_name='period_start',
        lookup_expr='gte',
        label='Начало периода от'
    )
    
    period_end = django_filters.DateFilter(
        field_name='period_end',
        lookup_expr='lte',
        label='Конец периода до'
    )
    
    class Meta:
        model = CachedAnalytics
        fields = ['cache_type', 'period_start', 'period_end']


class ReportPresetFilter(django_filters.FilterSet):
    """
    Фильтры для пресетов отчетов
    """
    
    report_type = django_filters.ChoiceFilter(
        choices=ReportPreset.REPORT_TYPES,
        label='Тип отчета'
    )
    
    is_default = django_filters.BooleanFilter(
        field_name='is_default',
        label='Пресет по умолчанию'
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
        model = ReportPreset
        fields = ['report_type', 'is_default', 'created_after', 'created_before']