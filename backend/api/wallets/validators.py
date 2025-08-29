# evercoin/backend/api/wallets/validators.py
from rest_framework import serializers

def validate_wallet_name_uniqueness(user, name, exclude_pk=None):
    """Проверка уникальности названия счета для пользователя"""
    queryset = user.wallets.all()
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    
    if queryset.filter(name=name).exists():
        raise serializers.ValidationError("Счет с таким названием уже существует")
    return name

def validate_positive_balance(value):
    """Проверка что баланс не отрицательный"""
    if value < 0:
        raise serializers.ValidationError("Баланс не может быть отрицательным")
    return value

def validate_sufficient_balance(wallet, amount):
    """Проверка достаточности средств на счете"""
    if wallet.balance < amount:
        raise serializers.ValidationError("На счете недостаточно средств")
    return True
