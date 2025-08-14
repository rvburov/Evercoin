from django.contrib import admin
from .models import Operation


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'type', 'date', 'user', 'wallet')
    list_filter = ('type', 'date', 'user', 'wallet')
    search_fields = ('title', 'comment', 'user__email')
    date_hierarchy = 'date'
    ordering = ('-date',)
