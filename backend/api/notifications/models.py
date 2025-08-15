# project/backend/api/notifications/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from operations.models import Operation
from users.models import User

class Notification(models.Model):
    """
    Модель уведомления о предстоящих операциях.
    Связана с операцией и содержит информацию о статусе прочтения.
    """
    NOTIFICATION_TYPES = (
        ('upcoming', _('Предстоящая операция')),
        ('reminder', _('Напоминание')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Пользователь')
    )
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Операция')
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='upcoming',
        verbose_name=_('Тип уведомления')
    )
    title = models.CharField(
        max_length=255,
        default=_('Скоро регулярный платеж'),
        verbose_name=_('Заголовок уведомления')
    )
    message = models.TextField(
        blank=True,
        verbose_name=_('Текст уведомления')
    )
    notification_date = models.DateTimeField(
        verbose_name=_('Дата уведомления'),
        help_text=_('Когда должно быть показано уведомление')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Прочитано')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-notification_date']
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['notification_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.operation.name}"

    def mark_as_read(self):
        """Пометить уведомление как прочитанное"""
        self.is_read = True
        self.save()
