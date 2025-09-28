# evercoin/backend/api/wallets/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_wallet_name_unique_per_user(value, user):
    """
    Валидация уникальности названия счета для пользователя
    """
    from .models import Wallet
    
    if Wallet.objects.filter(user=user, name=value).exists():
        raise ValidationError(_('У вас уже есть счет с таким названием'))


def validate_positive_initial_balance(value):
    """
    Валидация положительного начального баланса
    """
    if value < 0:
        raise ValidationError(_('Начальный баланс не может быть отрицательным'))


def validate_wallet_currency(value):
    """
    Валидация валюты счета
    """
    from api.core.constants.currencies import CURRENCY_CHOICES
    
    valid_currencies = [currency[0] for currency in CURRENCY_CHOICES]
    if value not in valid_currencies:
        raise ValidationError(_('Недопустимая валюта счета'))


def validate_transfer_amount(value):
    """
    Валидация суммы перевода
    """
    if value <= 0:
        raise ValidationError(_('Сумма перевода должна быть положительной'))
    
    if value > 1000000:  # Максимальная сумма перевода
        raise ValidationError(_('Сумма перевода слишком велика'))