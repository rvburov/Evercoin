# evercoin/backend/api/operations/admin.py
from django.contrib import admin
from .models import Operation


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    """
    Админ-панель для операций
    """
    list_display = [
        'title', 
        'amount', 
        'operation_type', 
        'wallet', 
        'category', 
        'operation_date', 
        'user'
    ]
    
    list_filter = [
        'operation_type', 
        'wallet', 
        'category', 
        'operation_date',
        'created_at'
    ]
    
    search_fields = [
        'title', 
        'description',
        'user__email',
        'user__username'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    date_hierarchy = 'operation_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'title', 
                'amount', 
                'operation_type',
                'operation_date'
            )
        }),
        ('Дополнительная информация', {
            'fields': (
                'description',
                'wallet',
                'category',
                'transfer_to_wallet'
            )
        }),
        ('Системная информация', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
