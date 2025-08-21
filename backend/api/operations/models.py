from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Operation(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'
    
    OPERATION_TYPES = [
        (INCOME, 'Доход'),
        (EXPENSE, 'Расход'),
        (TRANSFER, 'Перевод'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='operations')
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='operations')
    
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Для переводов
    transfer_to_wallet = models.ForeignKey(
        'wallets.Wallet', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transfer_operations'
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'operation_type']),
            models.Index(fields=['user', 'wallet']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.amount} ({self.operation_type})"
    
    def save(self, *args, **kwargs):
        # Обновляем баланс кошелька при создании/обновлении операции
        if not self.pk:
            old_amount = Decimal('0')
        else:
            old_operation = Operation.objects.get(pk=self.pk)
            old_amount = old_operation.amount
        
        super().save(*args, **kwargs)
        
        # Обновляем баланс кошелька
        if self.operation_type == self.INCOME:
            self.wallet.balance += (self.amount - old_amount)
        elif self.operation_type == self.EXPENSE:
            self.wallet.balance -= (self.amount - old_amount)
        elif self.operation_type == self.TRANSFER and self.transfer_to_wallet:
            self.wallet.balance -= (self.amount - old_amount)
            self.transfer_to_wallet.balance += (self.amount - old_amount)
            self.transfer_to_wallet.save()
        
        self.wallet.save()
