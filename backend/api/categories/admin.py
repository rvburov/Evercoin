# project/backend/api/categories/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки админ-панели для модели Category"""
    list_display = (
        'name', 'user', 'type', 
        'parent', 'is_system', 'created_at'
    )
    list_filter = ('type', 'is_system')
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'type', 'parent')
        }),
        ('Визуальное оформление', {
            'fields': ('icon', 'color')
        }),
        ('Системные настройки', {
            'fields': ('is_system',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Оптимизация запросов к БД"""
        return super().get_queryset(request).select_related('user', 'parent')
