# evercoin/backend/api/categories/admin.py
from django.contrib import admin
from .models import Category, CategoryMerge


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админ-панель для категорий
    """
    list_display = [
        'name', 
        'user', 
        'category_type', 
        'icon', 
        'is_default',
        'is_active',
        'operation_count',
        'created_at'
    ]
    
    list_filter = [
        'category_type', 
        'is_default', 
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'user__email',
        'user__username',
        'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'operation_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'name', 
                'category_type',
            )
        }),
        ('Внешний вид', {
            'fields': (
                'icon',
                'color'
            )
        }),
        ('Настройки', {
            'fields': (
                'is_default',
                'is_active',
                'description'
            )
        }),
        ('Статистика', {
            'fields': (
                'operation_count',
            ),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Оптимизация запроса для админки
        """
        return super().get_queryset(request).select_related('user')
    
    def operation_count(self, obj):
        """
        Отображение количества операций
        """
        return obj.operations.count()
    operation_count.short_description = 'Кол-во операций'


@admin.register(CategoryMerge)
class CategoryMergeAdmin(admin.ModelAdmin):
    """
    Админ-панель для слияний категорий
    """
    list_display = [
        'from_category', 
        'to_category', 
        'user',
        'operation_count',
        'merged_at'
    ]
    
    list_filter = [
        'merged_at'
    ]
    
    search_fields = [
        'from_category__name',
        'to_category__name',
        'user__email'
    ]
    
    readonly_fields = ['merged_at']
    
    fieldsets = (
        ('Информация о слиянии', {
            'fields': (
                'user',
                'from_category',
                'to_category',
                'operation_count'
            )
        }),
        ('Системная информация', {
            'fields': ('merged_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Оптимизация запроса для админки
        """
        return super().get_queryset(request).select_related('user', 'from_category', 'to_category')