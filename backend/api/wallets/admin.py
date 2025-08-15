# project/backend/api/notifications/admin.py
from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Настройки админ-панели для модели Wallet"""
    list_display = (
        'name', 'user', 'balance', 
        'currency', 'is_default', 'exclude_from_total'
    )
    list_filter = ('currency', 'is_default', 'exclude_from_total')
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'balance', 'currency')
        }),
        ('Настройки отображения', {
            'fields': ('icon', 'color', 'is_default', 'exclude_from_total')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Оптимизация запросов к БД"""
        return super().get_queryset(request).select_related('user')
