# evercoin/backend/api/analytics/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class CachedAnalytics(models.Model):
    """
    Модель для кеширования аналитических данных для улучшения производительности
    """
    
    CACHE_TYPES = [
        ('monthly_summary', 'Сводка за месяц'),
        ('category_stats', 'Статистика по категориям'),
        ('daily_stats', 'Дневная статистика'),
        ('trends', 'Тренды за 6 месяцев'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='cached_analytics',
        verbose_name='Пользователь'
    )
    
    cache_type = models.CharField(
        max_length=20,
        choices=CACHE_TYPES,
        verbose_name='Тип кеша'
    )
    
    period_start = models.DateField(
        verbose_name='Начало периода'
    )
    
    period_end = models.DateField(
        verbose_name='Конец периода'
    )
    
    data = models.JSONField(
        verbose_name='Данные аналитики'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Время истечения срока действия'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Кешированная аналитика'
        verbose_name_plural = 'Кешированная аналитика'
        unique_together = ['user', 'cache_type', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['user', 'cache_type', 'expires_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.get_cache_type_display()} - {self.user}"
    
    def save(self, *args, **kwargs):
        """
        Устанавливаем время истечения срока действия при сохранении
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)  # Кеш на 1 час
        super().save(*args, **kwargs)
    
    @classmethod
    def get_cached_data(cls, user, cache_type, period_start, period_end):
        """
        Получение кешированных данных
        """
        now = timezone.now()
        try:
            cached = cls.objects.get(
                user=user,
                cache_type=cache_type,
                period_start=period_start,
                period_end=period_end,
                expires_at__gt=now
            )
            return cached.data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, user, cache_type, period_start, period_end, data):
        """
        Сохранение данных в кеш
        """
        now = timezone.now()
        expires_at = now + timedelta(hours=1)
        
        cached, created = cls.objects.update_or_create(
            user=user,
            cache_type=cache_type,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'data': data,
                'expires_at': expires_at
            }
        )
        return cached


class ReportPreset(models.Model):
    """
    Модель для сохранения пресетов отчетов
    """
    
    REPORT_TYPES = [
        ('monthly', 'Ежемесячный отчет'),
        ('category', 'Отчет по категориям'),
        ('trends', 'Тренды'),
        ('custom', 'Пользовательский отчет'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='report_presets',
        verbose_name='Пользователь'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Название пресета'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        verbose_name='Тип отчета'
    )
    
    filters = models.JSONField(
        verbose_name='Параметры фильтрации'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Пресет по умолчанию'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Пресет отчета'
        verbose_name_plural = 'Пресеты отчетов'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.user}"
    
    def save(self, *args, **kwargs):
        """
        Если это пресет по умолчанию, снимаем флаг с других пресетов пользователя
        """
        if self.is_default:
            ReportPreset.objects.filter(
                user=self.user, 
                report_type=self.report_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)