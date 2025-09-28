# evercoin/backend/api/wallets/admin.py
from django.contrib import admin
from .models import Wallet, WalletTransfer


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Админ-панель для счетов
    """
    list_display = [
        'name', 
        'user', 
        'balance', 
        'currency', 
        'is_default', 
        'is_hidden',
        'created_at'
    ]
    
    list_filter = [
        'currency', 
        'is_default', 
        'is_hidden',
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'user__email',
        'user__username',
        'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'initial_balance']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'name', 
                'balance', 
                'currency',
                'initial_balance'
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
                'is_hidden',
                'description'
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
    
    def get_queryset(self, request):
        """
        Оптимизация запроса для админки
        """
        return super().get_queryset(request).select_related('user')


@admin.register(WalletTransfer)
class WalletTransferAdmin(admin.ModelAdmin):
    """
    Админ-панель для переводов между счетами
    """
    list_display = [
        'from_wallet', 
        'to_wallet', 
        'amount', 
        'user',
        'transfer_date'
    ]
    
    list_filter = [
        'transfer_date',
        'created_at'
    ]
    
    search_fields = [
        'from_wallet__name',
        'to_wallet__name',
        'user__email',
        'description'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация о переводе', {
            'fields': (
                'user',
                'from_wallet',
                'to_wallet',
                'amount',
                'description',
                'transfer_date'
            )
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Оптимизация запроса для админки
        """
        return super().get_queryset(request).select_related('user', 'from_wallet', 'to_wallet')