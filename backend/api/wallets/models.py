# evercoin/backend/api/wallets/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.core.constants.icons import WALLET_ICONS
from api.core.constants.colors import COLORS

User = get_user_model()

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    icon = models.CharField(max_length=50, choices=WALLET_ICONS, default='wallet')
    color = models.CharField(max_length=7, choices=COLORS, default='#3B82F6')
    is_default = models.BooleanField(default=False)
    exclude_from_total = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=3, default='RUB')  # RUB, USD, EUR и т.д.
    
    class Meta:
        ordering = ['-is_default', 'name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_wallet_name_per_user')
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.name} - {self.balance}"
    
    def save(self, *args, **kwargs):
        # Если этот кошелек становится основным, снимаем флаг с других кошельков пользователя
        if self.is_default:
            Wallet.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        from api.operations.models import Operation
        
        # Получаем счет по умолчанию для переноса операций
        default_wallet = Wallet.objects.filter(
            user=self.user, 
            is_default=True
        ).exclude(pk=self.pk).first()
        
        # Переносим операции на счет по умолчанию или оставляем без счета
        operations_to_update = Operation.objects.filter(wallet=self)
        if default_wallet:
            operations_to_update.update(wallet=default_wallet)
        else:
            operations_to_update.update(wallet=None)
        
        super().delete(*args, **kwargs)

class WalletTransfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transfers')
    from_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_wallet.name} → {self.to_wallet.name} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Проверяем достаточно ли средств на исходном счете
        if self.from_wallet.balance < self.amount:
            raise ValueError("На исходном счете недостаточно средств")
        
        # Выполняем перевод
        self.from_wallet.balance -= self.amount
        self.to_wallet.balance += self.amount
        
        self.from_wallet.save()
        self.to_wallet.save()
        
        super().save(*args, **kwargs)
