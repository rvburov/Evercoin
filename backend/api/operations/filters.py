import django_filters
from django.db.models import Q
from .models import Operation
from django.utils import timezone
from datetime import timedelta


class OperationFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type')
    wallet = django_filters.CharFilter(field_name='wallet__id')
    category = django_filters.CharFilter(field_name='category__id')
    search = django_filters.CharFilter(method='filter_search')
    period = django_filters.CharFilter(method='filter_period')

    class Meta:
        model = Operation
        fields = ['type', 'wallet', 'category', 'search', 'period']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(category__name__icontains=value) |
            Q(comment__icontains=value)
        )

    def filter_period(self, queryset, name, value):
        today = timezone.now().date()
        
        if value == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif value == 'month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif value == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif value == 'day':
            start_date = end_date = today
        else:
            return queryset
            
        return queryset.filter(date__date__range=[start_date, end_date])
