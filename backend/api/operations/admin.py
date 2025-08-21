# project/backend/api/operations/admin.py
from django.contrib import admin
from .models import Operation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'operation_type', 'user', 'wallet', 'date']
    list_filter = ['operation_type', 'date', 'wallet']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'wallet', 'category', 'transfer_to_wallet')
        }),
        ('Детали операции', {
            'fields': ('amount', 'title', 'description', 'operation_type', 'date')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
