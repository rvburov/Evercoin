# evercoin/backend/api/operations/models.py
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from api.categories.models import Category
from api.wallets.models import Wallet

User = get_user_model()


class Operation(models.Model):
    """Модель финансовой операции (доход/расход/перевод)."""

    OPERATION_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
        ('transfer', 'Перевод'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Пользователь'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    operation_type = models.CharField(
        max_length=10,
        choices=OPERATION_TYPES,
        verbose_name='Тип операции'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operations',
        verbose_name='Категория'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operations',
        verbose_name='Счет'
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата операции'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name='Повторяющаяся операция'
    )
    recurring_pattern = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Паттерн повторения'
    )

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'operation_type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'wallet']),
        ]
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __str__(self):
        return f"{self.user.email} - {self.title} - {self.amount}"

    def save(self, *args, **kwargs):
        """Автоматическое обновление баланса кошелька при сохранении."""
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Возврат суммы в кошелек при удалении операции."""
        super().delete(*args, **kwargs)


class OperationLog(models.Model):
    """Модель для логирования действий с операциями."""

    ACTION_CHOICES = (
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('duplicate', 'Дублирование'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='operation_logs',
        verbose_name='Пользователь'
    )
    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Операция'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Старые данные'
    )
    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Новые данные'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Лог операции'
        verbose_name_plural = 'Логи операций'

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.operation.title}"