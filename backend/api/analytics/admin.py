# evercoin/backend/api/analytics/admin.py
from django.contrib import admin
from .models import CachedAnalytics, ReportPreset


@admin.register(CachedAnalytics)
class CachedAnalyticsAdmin(admin.ModelAdmin):
    """
    Админ-панель для кешированной аналитики
    """
    list_display = [
        'user', 
        'cache_type', 
        'period_start', 
        'period_end',
        'expires_at',
        'created_at'
    ]
    
    list_filter = [
        'cache_type', 
        'period_start',
        'period_end',
        'expires_at',
        'created_at'
    ]
    
    search_fields = [
        'user__email',
        'user__username'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'cache_type',
                'period_start',
                'period_end'
            )
        }),
        ('Данные', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Срок действия', {
            'fields': ('expires_at',)
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


@admin.register(ReportPreset)
class ReportPresetAdmin(admin.ModelAdmin):
    """
    Админ-панель для пресетов отчетов
    """
    list_display = [
        'name', 
        'user', 
        'report_type', 
        'is_default',
        'created_at'
    ]
    
    list_filter = [
        'report_type', 
        'is_default',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'user__email',
        'user__username'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 
                'name', 
                'report_type',
            )
        }),
        ('Параметры', {
            'fields': ('filters',)
        }),
        ('Настройки', {
            'fields': ('is_default',)
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