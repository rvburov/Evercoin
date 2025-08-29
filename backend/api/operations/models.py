# evercoin/backend/api/operations/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.categories.models import Category
from api.wallets.models import Wallet

User = get_user_model()

class Operation(models.Model):
    OPERATION_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
        ('transfer', 'Перевод'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'operation_type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'wallet']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Обновляем баланс кошелька при создании/изменении операции
        old_amount = None
        old_wallet = None
        old_type = None
        
        if self.pk:
            try:
                old_operation = Operation.objects.get(pk=self.pk)
                old_amount = old_operation.amount
                old_wallet = old_operation.wallet
                old_type = old_operation.operation_type
                
                # Возвращаем старую сумму в кошелек
                if old_wallet:
                    if old_type == 'income':
                        old_wallet.balance -= old_amount
                    elif old_type == 'expense':
                        old_wallet.balance += old_amount
                    old_wallet.save()
            except Operation.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Обновляем баланс кошелька с новой суммой
        if self.wallet:
            if self.operation_type == 'income':
                self.wallet.balance += self.amount
            elif self.operation_type == 'expense':
                if self.wallet.balance < self.amount:
                    # Откатываем сохранение если недостаточно средств
                    if old_wallet and old_amount:
                        if old_type == 'income':
                            old_wallet.balance += old_amount
                        elif old_type == 'expense':
                            old_wallet.balance -= old_amount
                        old_wallet.save()
                    raise ValueError("На счету недостаточно средств")
                self.wallet.balance -= self.amount
            self.wallet.save()
    
    def delete(self, *args, **kwargs):
        # Возвращаем сумму в кошелек при удалении операции
        if self.wallet:
            if self.operation_type == 'income':
                self.wallet.balance -= self.amount
            elif self.operation_type == 'expense':
                self.wallet.balance += self.amount
            self.wallet.save()
        
        super().delete(*args, **kwargs)

class OperationLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('duplicate', 'Дублирование'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operation_logs')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.operation.title}"
