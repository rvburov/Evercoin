# project/backend/api/categories/filters.py
import django_filters
from .models import Category

class CategoryFilter(django_filters.FilterSet):
    """Фильтры для списка категорий"""
    type = django_filters.ChoiceFilter(
        choices=Category.TYPE_CHOICES,
        label='Тип категории'
    )
    parent = django_filters.NumberFilter(
        field_name='parent__id',
        label='ID родительской категории'
    )
    has_parent = django_filters.BooleanFilter(
        field_name='parent',
        lookup_expr='isnull',
        exclude=True,
        label='Только с родительской категорией'
    )

    class Meta:
        model = Category
        fields = ['type', 'is_system']
