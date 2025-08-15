# project/backend/api/notifications/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from api.core.constants import currencies

class Wallet(models.Model):
    """
    Модель финансового счета пользователя.
    Хранит информацию о балансе, валюте и настройках отображения.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name=_('Пользователь')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название счета'),
        help_text=_('Например: Основной счет, Кредитная карта и т.д.')
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Баланс')
    )
    currency = models.CharField(
        max_length=3,
        choices=currencies.CURRENCY_CHOICES,
        default=currencies.DEFAULT_CURRENCY,
        verbose_name=_('Валюта')
    )
    icon = models.CharField(
        max_length=50,
        default='wallet',
        verbose_name=_('Иконка'),
        help_text=_('Код иконки из доступного набора')
    )
    color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        verbose_name=_('Цвет фона'),
        help_text=_('HEX-код цвета, например #FF5733')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Счет по умолчанию')
    )
    exclude_from_total = models.BooleanField(
        default=False,
        verbose_name=_('Не учитывать в общем балансе'),
        help_text=_('Если включено, баланс этого счета не будет влиять на общую сумму')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Счет')
        verbose_name_plural = _('Счета')
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_wallet_name_per_user'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.currency}): {self.balance}"

    def save(self, *args, **kwargs):
        """При сохранении гарантируем, что у пользователя только один счет по умолчанию"""
        if self.is_default:
            Wallet.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
