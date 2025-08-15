# project/backend/api/notifications/serializers.py
from rest_framework import serializers
from .models import Wallet
from api.core.constants import icons, colors

class WalletSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для счетов.
    Включает все поля и валидацию.
    """
    available_icons = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            'id', 'name', 'balance', 'currency', 
            'icon', 'color', 'is_default', 
            'exclude_from_total', 'created_at',
            'available_icons', 'available_colors'
        ]
        read_only_fields = ['created_at', 'balance']

    def get_available_icons(self, obj):
        """Возвращает список доступных иконок для фронтенда"""
        return icons.WALLET_ICONS

    def get_available_colors(self, obj):
        """Возвращает список доступных цветов для фронтенда"""
        return colors.WALLET_COLORS

    def validate(self, data):
        """Дополнительная валидация данных счета"""
        if 'balance' in data and data['balance'] < 0:
            raise serializers.ValidationError(
                {'balance': 'Баланс не может быть отрицательным'}
            )
        return data

class SimpleWalletSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для использования в других моделях.
    Содержит только основные поля.
    """
    class Meta:
        model = Wallet
        fields = ['id', 'name', 'balance', 'currency', 'icon', 'color']
        read_only_fields = fields

class WalletTransferSerializer(serializers.Serializer):
    """
    Сериализатор для операции перевода между счетами.
    """
    from_wallet = serializers.PrimaryKeyRelatedField(
        queryset=Wallet.objects.all(),
        required=True
    )
    to_wallet = serializers.PrimaryKeyRelatedField(
        queryset=Wallet.objects.all(),
        required=True
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        required=True
    )
    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    def validate(self, data):
        """Проверка возможности перевода"""
        from_wallet = data['from_wallet']
        to_wallet = data['to_wallet']
        amount = data['amount']

        if from_wallet == to_wallet:
            raise serializers.ValidationError(
                {'to_wallet': 'Нельзя перевести на тот же счет'}
            )

        if from_wallet.balance < amount:
            raise serializers.ValidationError(
                {'amount': f'Недостаточно средств. Доступно: {from_wallet.balance}'}
            )

        return data
