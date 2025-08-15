# project/backend/api/notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Настройки админ-панели для модели Notification"""
    list_display = (
        'title', 'user', 'operation', 
        'notification_type', 'is_read', 'notification_date'
    )
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'user__email', 'operation__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'operation', 'notification_type')
        }),
        ('Содержание', {
            'fields': ('title', 'message')
        }),
        ('Статус', {
            'fields': ('is_read', 'notification_date')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        """Действие для пометки выбранных уведомлений как прочитанных"""
        updated = queryset.update(is_read=True)
        self.message_user(
            request, 
            f"{updated} уведомлений помечены как прочитанные"
        )
    mark_as_read.short_description = "Пометить как прочитанные"

    def get_queryset(self, request):
        """Оптимизация запросов к БД"""
        return super().get_queryset(request).select_related('user', 'operation')
