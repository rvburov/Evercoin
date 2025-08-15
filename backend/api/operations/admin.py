# project/backend/api/operations/admin.py
from django.contrib import admin
from .models import Operation, RecurringOperation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    """Админка для операций с фильтрацией по типам и датам"""
    list_display = ('name', 'amount', 'operation_type', 'category', 'wallet', 'date')
    list_filter = ('operation_type', 'date', 'category')
    search_fields = ('name', 'description')
    date_hierarchy = 'date'
    ordering = ('-date',)
    raw_id_fields = ('wallet', 'category')

@admin.register(RecurringOperation)
class RecurringOperationAdmin(admin.ModelAdmin):
    """Админка для повторяющихся операций с фильтрацией по периодичности"""
    list_display = ('base_operation', 'next_date', 'interval')
    list_filter = ('interval',)
    search_fields = ('base_operation__name',)
