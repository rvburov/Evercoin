# evercoin/backend/api/operations/admin.py
from django.contrib import admin
from .models import Operation, OperationLog

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'amount', 'operation_type', 'category', 'wallet', 'date']
    list_filter = ['operation_type', 'date', 'category', 'wallet', 'is_recurring']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'amount', 'description', 'operation_type')
        }),
        ('Категория и счет', {
            'fields': ('category', 'wallet')
        }),
        ('Даты', {
            'fields': ('date', 'created_at', 'updated_at')
        }),
        ('Повторяющаяся операция', {
            'fields': ('is_recurring', 'recurring_pattern'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'operation', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email', 'operation__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация о действии', {
            'fields': ('user', 'operation', 'action')
        }),
        ('Данные', {
            'fields': ('old_data', 'new_data'),
            'classes': ('collapse',)
        }),
        ('Дата', {
            'fields': ('created_at',)
        }),
    )
