# evercoin/backend/api/operations//validators.py
from rest_framework import serializers
from datetime import datetime
from django.utils import timezone

def validate_positive_amount(value):
    """Валидация положительной суммы"""
    if value <= 0:
        raise serializers.ValidationError("Сумма операции должна быть положительной")
    return value

def validate_future_date(value):
    """Валидация даты (не может быть в будущем)"""
    if value > timezone.now():
        raise serializers.ValidationError("Дата операции не может быть в будущем")
    return value

def validate_wallet_balance(wallet, amount, operation_type):
    """Валидация баланса кошелька"""
    if operation_type == 'expense' and wallet.balance < amount:
        raise serializers.ValidationError("На счету недостаточно средств")
    return True

def validate_recurring_pattern(value):
    """Валидация паттерна повторяющейся операции"""
    if value:
        required_fields = ['frequency', 'interval']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Поле {field} обязательно для повторяющихся операций")
        
        if value['frequency'] not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise serializers.ValidationError("Недопустимая частота повторения")
    
    return value
