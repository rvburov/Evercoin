# project/backend/api/operations/validators.py
from django.core.exceptions import ValidationError
from wallets.models import Wallet

def validate_wallet_balance(wallet_id, amount, operation_type):
    """Проверка достаточности средств на счете для расходной операции"""
    if operation_type != 'expense':
        return
    
    wallet = Wallet.objects.get(pk=wallet_id)
    if wallet.balance < amount:
        raise ValidationError(
            f'Недостаточно средств на счете. Доступно: {wallet.balance}'
        )

def validate_recurring_dates(start_date, end_date):
    """Проверка корректности дат для повторяющейся операции"""
    if end_date and end_date <= start_date:
        raise ValidationError(
            'Дата окончания должна быть позже даты начала'
        )
