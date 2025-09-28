# evercoin/backend/api/operations/validators.py
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime


def validate_operation_date(value):
    """
    Валидация даты операции (не может быть в будущем)
    """
    if value > timezone.now():
        raise ValidationError('Дата операции не может быть в будущем')


def validate_positive_amount(value):
    """
    Валидация положительной суммы операции
    """
    if value <= 0:
        raise ValidationError('Сумма операции должна быть положительной')


def validate_operation_type(value):
    """
    Валидация типа операции
    """
    valid_types = ['income', 'expense', 'transfer']
    if value not in valid_types:
        raise ValidationError(f'Недопустимый тип операции. Допустимые значения: {", ".join(valid_types)}')
