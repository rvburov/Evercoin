# evercoin/backend/api/operations/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.core.constants.currencies import CURRENCIES

User = get_user_model()


class Operation(models.Model):
    """
    Модель финансовой операции (доход, расход, перевод)
    """
    
    OPERATION_TYPES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
        ('transfer', 'Перевод'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='operations',
        verbose_name='Пользователь'
    )
    
    title = models.CharField(
        max_length=200, 
        verbose_name='Название операции'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма операции'
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Комментарий к операции'
    )
    
    operation_type = models.CharField(
        max_length=10,
        choices=OPERATION_TYPES,
        verbose_name='Тип операции'
    )
    
    operation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата операции'
    )
    
    wallet = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Счет операции'
    )
    
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='operations',
        verbose_name='Категория операции'
    )
    
    # Для переводов между счетами
    transfer_to_wallet = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='transfer_operations',
        verbose_name='Счет назначения (для переводов)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'
        ordering = ['-operation_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'operation_date']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['wallet']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.operation_type})"
    
    def save(self, *args, **kwargs):
        """
        Переопределение сохранения для обновления баланса счета
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Получаем старую операцию для сравнения
            old_operation = None
            if self.pk:
                try:
                    old_operation = Operation.objects.get(pk=self.pk)
                except Operation.DoesNotExist:
                    pass
            
            # Сохраняем операцию
            super().save(*args, **kwargs)
            
            # Обновляем баланс счета
            self._update_wallet_balance(old_operation)
    
    def delete(self, *args, **kwargs):
        """
        Переопределение удаления для обновления баланса счета
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Сохраняем данные для обновления баланса
            wallet = self.wallet
            amount = self.amount
            operation_type = self.operation_type
            
            # Удаляем операцию
            super().delete(*args, **kwargs)
            
            # Обновляем баланс счета
            if operation_type == 'income':
                wallet.balance -= amount
            elif operation_type == 'expense':
                wallet.balance += amount
            # Для переводов баланс уже обновлен в операции назначения
            
            wallet.save()
    
    def _update_wallet_balance(self, old_operation=None):
        """
        Внутренний метод для обновления баланса счета
        """
        wallet = self.wallet
        
        if old_operation:
            # Откатываем старую операцию
            old_amount = old_operation.amount
            old_type = old_operation.operation_type
            
            if old_type == 'income':
                wallet.balance -= old_amount
            elif old_type == 'expense':
                wallet.balance += old_amount
        
        # Применяем новую операцию
        if self.operation_type == 'income':
            wallet.balance += self.amount
        elif self.operation_type == 'expense':
            wallet.balance -= self.amount
        
        wallet.save()
        
        # Для переводов создаем вторую операцию
        if self.operation_type == 'transfer' and self.transfer_to_wallet:
            self._create_transfer_operation()
    
    def _create_transfer_operation(self):
        """
        Создание парной операции для перевода между счетами
        """
        # Проверяем, не создана ли уже парная операция
        if not hasattr(self, 'paired_transfer'):
            Operation.objects.create(
                user=self.user,
                title=f"Перевод: {self.title}",
                amount=self.amount,
                description=self.description,
                operation_type='income',  # Для счета назначения это доход
                operation_date=self.operation_date,
                wallet=self.transfer_to_wallet,
                category=None,
                transfer_to_wallet=None  # Избегаем рекурсии
            )
    
    def clean(self):
        """
        Валидация данных перед сохранением
        """
        from django.core.exceptions import ValidationError
        
        # Проверка, что пользователь является владельцем счета
        if self.wallet.user != self.user:
            raise ValidationError({'wallet': 'Вы не являетесь владельцем этого счета'})
        
        # Проверка категории
        if self.category and self.category.user != self.user:
            raise ValidationError({'category': 'Вы не являетесь владельцем этой категории'})
        
        # Проверка счета назначения для переводов
        if self.operation_type == 'transfer':
            if not self.transfer_to_wallet:
                raise ValidationError({'transfer_to_wallet': 'Для перевода необходимо указать счет назначения'})
            if self.transfer_to_wallet.user != self.user:
                raise ValidationError({'transfer_to_wallet': 'Вы не являетесь владельцем счета назначения'})
            if self.wallet == self.transfer_to_wallet:
                raise ValidationError({'transfer_to_wallet': 'Нельзя переводить на тот же счет'})
        
        # Проверка баланса для расходов
        if self.operation_type == 'expense' and self.amount > self.wallet.balance:
            raise ValidationError({'amount': 'На счету недостаточно средств'})
