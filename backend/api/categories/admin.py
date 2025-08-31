# evercoin/backend/api/categories/admin.py
from django.contrib import admin

from .models import Category, CategoryBudget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий."""
    
    list_display = [
        'user',
        'name',
        'type',
        'icon',
        'color',
        'parent',
        'is_default',
        'created_at'
    ]
    list_filter = ['type', 'is_default', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'type', 'parent')
        }),
        ('Внешний вид', {
            'fields': ('icon', 'color')
        }),
        ('Дополнительно', {
            'fields': ('budget_limit', 'description', 'is_default')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    """Админ-панель для бюджетов категорий."""
    
    list_display = [
        'user',
        'category',
        'amount',
        'period',
        'is_active',
        'created_at'
    ]
    list_filter = ['period', 'is_active', 'created_at']
    search_fields = ['category__name', 'user__email']
    readonly_fields = [
        'created_at',
        'updated_at',
        'spent_amount',
        'remaining_amount'
    ]
    
    fieldsets = (
        ('Информация о бюджете', {
            'fields': ('user', 'category', 'amount', 'period')
        }),
        ('Период', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Статистика', {
            'fields': ('spent_amount', 'remaining_amount'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )