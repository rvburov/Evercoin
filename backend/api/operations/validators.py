# project/backend/api/operations/validators.py

from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone

def validate_date_range(start_date, end_date):
    """Валидация диапазона дат"""
    if start_date and end_date and start_date > end_date:
        raise serializers.ValidationError("Дата начала не может быть позже даты окончания")
    
    # Максимальный диапазон - 5 лет
    if start_date and end_date and (end_date - start_date).days > 1825:
        raise serializers.ValidationError("Максимальный диапазон - 5 лет")

def validate_operation_amount(amount, operation_type, wallet_balance):
    """Валидация суммы операции"""
    if amount <= 0:
        raise serializers.ValidationError("Сумма должна быть положительной")
    
    if operation_type == 'expense' and amount > wallet_balance:
        raise serializers.ValidationError("Недостаточно средств на счете")
    
    return amount
