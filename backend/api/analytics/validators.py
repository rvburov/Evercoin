# evercoin/backend/api/analytics/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_date_range(start_date, end_date):
    """
    Валидация диапазона дат
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError(_('Дата начала не может быть позже даты окончания'))
    
    if start_date and end_date and (end_date - start_date).days > 365:
        raise ValidationError(_('Период не может превышать 1 год'))


def validate_period_value(value):
    """
    Валидация значения периода
    """
    valid_periods = ['day', 'week', 'month', 'year', 'custom']
    if value not in valid_periods:
        raise ValidationError(_('Недопустимое значение периода'))


def validate_wallet_ids(value, user):
    """
    Валидация ID счетов
    """
    from api.wallets.models import Wallet
    
    if value:
        wallet_ids = set(value)
        user_wallet_ids = set(Wallet.objects.filter(user=user).values_list('id', flat=True))
        
        if not wallet_ids.issubset(user_wallet_ids):
            raise ValidationError(_('Указаны неверные ID счетов'))


def validate_category_ids(value, user):
    """
    Валидация ID категорий
    """
    from api.categories.models import Category
    
    if value:
        category_ids = set(value)
        user_category_ids = set(Category.objects.filter(user=user).values_list('id', flat=True))
        
        if not category_ids.issubset(user_category_ids):
            raise ValidationError(_('Указаны неверные ID категорий'))


def validate_operation_types(value):
    """
    Валидация типов операций
    """
    valid_types = ['income', 'expense', 'transfer']
    if value:
        for op_type in value:
            if op_type not in valid_types:
                raise ValidationError(_('Недопустимый тип операции'))