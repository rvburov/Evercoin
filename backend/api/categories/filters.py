import django_filters
from .models import Category


class CategoryFilter(django_filters.FilterSet):
    """
    Фильтры для категорий
    """
    
    category_type = django_filters.ChoiceFilter(
        choices=Category.CATEGORY_TYPES,
        label='Тип категории'
    )
    
    is_default = django_filters.BooleanFilter(
        field_name='is_default',
        label='Системная категория'
    )
    
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Активная категория'
    )
    
    has_operations = django_filters.BooleanFilter(
        method='filter_has_operations',
        label='Есть операции'
    )
    
    created_after = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Создана после'
    )
    
    created_before = django_filters.DateFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Создана до'
    )
    
    class Meta:
        model = Category
        fields = [
            'category_type',
            'is_default',
            'is_active',
            'has_operations',
            'created_after',
            'created_before'
        ]
    
    def filter_has_operations(self, queryset, name, value):
        """
        Фильтр по наличию операций
        """
        if value:
            return queryset.filter(operations__isnull=False).distinct()
        else:
            return queryset.filter(operations__isnull=True)