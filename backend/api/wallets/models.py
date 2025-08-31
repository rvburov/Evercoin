# evercoin/backend/api/wallets/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from api.core.constants.icons import WALLET_ICONS
from api.core.constants.colors import COLORS

User = get_user_model()


class Wallet(models.Model):
    """Модель счета пользователя."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name='Пользователь',
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название счета',
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Баланс',
    )
    icon = models.CharField(
        max_length=50,
        choices=WALLET_ICONS,
        default='wallet',
        verbose_name='Иконка',
    )
    color = models.CharField(
        max_length=7,
        choices=COLORS,
        default='#3B82F6',
        verbose_name='Цвет',
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Счет по умолчанию',
    )
    exclude_from_total = models.BooleanField(
        default=False,
        verbose_name='Исключить из общего баланса',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )
    currency = models.CharField(
        max_length=3,
        default='RUB',
        verbose_name='Валюта',
    )
    
    class Meta:
        ordering = ['-is_default', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_wallet_name_per_user',
            ),
        ]
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
    
    def __str__(self):
        return f"{self.user.email} - {self.name} - {self.balance}"
    
    def save(self, *args, **kwargs):
        """Сохранение с обработкой счета по умолчанию."""
        if self.is_default:
            Wallet.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Удаление счета с переносом операций на счет по умолчанию."""
        from api.operations.models import Operation
        
        default_wallet = Wallet.objects.filter(
            user=self.user,
            is_default=True,
        ).exclude(pk=self.pk).first()
        
        operations_to_update = Operation.objects.filter(wallet=self)
        if default_wallet:
            operations_to_update.update(wallet=default_wallet)
        else:
            operations_to_update.update(wallet=None)
        
        super().delete(*args, **kwargs)


class WalletTransfer(models.Model):
    """Модель перевода между счетами."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallet_transfers',
        verbose_name='Пользователь',
    )
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers',
        verbose_name='Счет отправителя',
    )
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
        verbose_name='Счет получателя',
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма перевода',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Перевод между счетами'
        verbose_name_plural = 'Переводы между счетами'
    
    def __str__(self):
        return f"{self.from_wallet.name} → {self.to_wallet.name} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Сохранение перевода с проверкой средств и обновлением балансов."""
        if self.from_wallet.balance < self.amount:
            raise ValueError("На исходном счете недостаточно средств")
        
        self.from_wallet.balance -= self.amount
        self.to_wallet.balance += self.amount
        
        self.from_wallet.save()
        self.to_wallet.save()
        
        super().save(*args, **kwargs)