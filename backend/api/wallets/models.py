# evercoin/backend/api/wallets/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.core.constants.currencies import CURRENCY_CHOICES
from api.core.constants.icons import WALLET_ICONS
from api.core.constants.colors import COLORS

User = get_user_model()


class Wallet(models.Model):
    """
    Модель финансового счета (кошелька)
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallets',
        verbose_name='Пользователь'
    )
    
    name = models.CharField(
        max_length=100, 
        verbose_name='Название счета'
    )
    
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(-1000000)],  # Разрешаем отрицательный баланс для кредитных счетов
        verbose_name='Баланс счета'
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='RUB',
        verbose_name='Валюта счета'
    )
    
    icon = models.CharField(
        max_length=50,
        choices=WALLET_ICONS,
        default='wallet',
        verbose_name='Иконка счета'
    )
    
    color = models.CharField(
        max_length=7,
        choices=COLORS,
        default='#4ECDC4',
        verbose_name='Цвет счета'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Счет по умолчанию'
    )
    
    is_hidden = models.BooleanField(
        default=False,
        verbose_name='Не показывать в общем балансе'
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Описание счета'
    )
    
    initial_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Начальный баланс'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
        ordering = ['-is_default', '-created_at']
        unique_together = ['user', 'name']  # Уникальное название счета для каждого пользователя
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['user', 'is_hidden']),
            models.Index(fields=['currency']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.balance} {self.currency}"
    
    def save(self, *args, **kwargs):
        """
        Переопределение сохранения для обработки счета по умолчанию
        """
        # Если этот счет помечен как default, снимаем флаг с других счетов пользователя
        if self.is_default:
            Wallet.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        # При первом создании счета устанавливаем начальный баланс
        if not self.pk and self.initial_balance != 0:
            self.balance = self.initial_balance
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Переопределение удаления с проверкой связанных операций
        """
        from api.operations.models import Operation
        
        # Проверяем, есть ли связанные операции
        operation_count = self.operations.count()
        transfer_operation_count = self.transfer_operations.count()
        total_operations = operation_count + transfer_operation_count
        
        if total_operations > 0:
            raise models.ProtectedError(
                "Нельзя удалить счет с привязанными операциями. "
                "Сначала удалите или перенесите операции.",
                self
            )
        
        # Если удаляемый счет был по умолчанию, назначаем новый default счет
        if self.is_default:
            other_wallets = Wallet.objects.filter(user=self.user).exclude(pk=self.pk)
            if other_wallets.exists():
                new_default = other_wallets.first()
                new_default.is_default = True
                new_default.save()
        
        super().delete(*args, **kwargs)
    
    @property
    def total_income(self):
        """
        Общая сумма доходов по счету
        """
        from django.db.models import Sum
        result = self.operations.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        return result
    
    @property
    def total_expense(self):
        """
        Общая сумма расходов по счету
        """
        from django.db.models import Sum
        result = self.operations.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        return result
    
    @property
    def net_flow(self):
        """
        Чистый поток средств (доходы - расходы)
        """
        return self.total_income - self.total_expense
    
    def get_balance_history(self, days=30):
        """
        Получение истории баланса за указанное количество дней
        """
        from django.db.models import Sum
        from api.operations.models import Operation
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Получаем ежедневные изменения баланса
        daily_changes = (
            Operation.objects
            .filter(wallet=self, operation_date__range=[start_date, end_date])
            .extra({'date': "date(operation_date)"})
            .values('date')
            .annotate(
                income=Sum('amount', filter=models.Q(operation_type='income')),
                expense=Sum('amount', filter=models.Q(operation_type='expense'))
            )
            .order_by('date')
        )
        
        return list(daily_changes)


class WalletTransfer(models.Model):
    """
    Модель для отслеживания переводов между счетами
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallet_transfers',
        verbose_name='Пользователь'
    )
    
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers',
        verbose_name='Счет отправителя'
    )
    
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
        verbose_name='Счет получателя'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма перевода'
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Описание перевода'
    )
    
    transfer_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата перевода'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Перевод между счетами'
        verbose_name_plural = 'Переводы между счетами'
        ordering = ['-transfer_date']
    
    def __str__(self):
        return f"Перевод {self.amount} из {self.from_wallet.name} в {self.to_wallet.name}"
    
    def clean(self):
        """
        Валидация данных перевода
        """
        from django.core.exceptions import ValidationError
        
        if self.from_wallet == self.to_wallet:
            raise ValidationError('Нельзя переводить средства на тот же счет')
        
        if self.from_wallet.currency != self.to_wallet.currency:
            raise ValidationError('Переводы между счетами в разных валютах не поддерживаются')
        
        if self.amount > self.from_wallet.balance:
            raise ValidationError('На счете отправителя недостаточно средств')