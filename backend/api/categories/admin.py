# project/backend/api/categories/admin.py
from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'operation_type', 'user', 'icon', 'color', 'created_at']
    list_filter = ['operation_type', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'operation_type')
        }),
        ('Внешний вид', {
            'fields': ('icon', 'color'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
