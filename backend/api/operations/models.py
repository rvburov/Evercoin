# project/backend/api/operations/models.py
from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from wallets.models import Wallet
from categories.models import Category

class Operation(models.Model):
    """Модель финансовой операции (доход/расход/перевод)"""
    OPERATION_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
        ('transfer', 'Перевод'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    name = models.CharField(max_length=255, verbose_name='Название операции')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма'
    )
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES, verbose_name='Тип операции')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='operations')
    date = models.DateTimeField(verbose_name='Дата операции')
    description = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['operation_type']),
        ]

    def __str__(self):
        return f"{self.name} - {self.amount}"

class RecurringOperation(models.Model):
    """Модель для повторяющихся операций с настройкой периодичности"""
    INTERVAL_CHOICES = (
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно'),
    )

    base_operation = models.OneToOneField(Operation, on_delete=models.CASCADE, related_name='recurring')
    next_date = models.DateTimeField(verbose_name='Следующая дата выполнения')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, verbose_name='Интервал')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')

    class Meta:
        ordering = ['next_date']

    def __str__(self):
        return f"Повторяющаяся: {self.base_operation.name}"
