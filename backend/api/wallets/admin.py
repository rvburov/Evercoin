# evercoin/backend/api/wallets/admin.py
from django.contrib import admin
from .models import Wallet, WalletTransfer

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'balance', 'currency', 'is_default', 'exclude_from_total', 'created_at']
    list_filter = ['is_default', 'exclude_from_total', 'currency', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'balance', 'currency')
        }),
        ('Внешний вид', {
            'fields': ('icon', 'color')
        }),
        ('Настройки', {
            'fields': ('is_default', 'exclude_from_total')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(WalletTransfer)
class WalletTransferAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_wallet', 'to_wallet', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['from_wallet__name', 'to_wallet__name', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация о переводе', {
            'fields': ('user', 'from_wallet', 'to_wallet', 'amount', 'description')
        }),
        ('Дата', {
            'fields': ('created_at',)
        }),
    )
