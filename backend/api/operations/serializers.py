# project/backend/api/operations/serializers.py
from rest_framework import serializers
from .models import Operation, RecurringOperation
from wallets.serializers import SimpleWalletSerializer
from categories.serializers import SimpleCategorySerializer

class OperationSerializer(serializers.ModelSerializer):
    """Сериализатор для операций с вложенными данными о счете и категории"""
    wallet = SimpleWalletSerializer(read_only=True)
    category = SimpleCategorySerializer(read_only=True)
    wallet_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Будет установлено в __init__
        source='wallet',
        write_only=True,
        required=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Будет установлено в __init__
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Operation
        fields = [
            'id', 'name', 'amount', 'operation_type', 
            'category', 'category_id', 'wallet', 'wallet_id',
            'date', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически устанавливаем queryset для wallet_id и category_id
        user = self.context['request'].user if 'request' in self.context else None
        if user:
            self.fields['wallet_id'].queryset = user.wallets.all()
            self.fields['category_id'].queryset = user.categories.all()

    def validate(self, data):
        """Дополнительная валидация данных операции"""
        if data.get('operation_type') == 'expense':
            wallet = data.get('wallet')
            amount = data.get('amount')
            if wallet and amount and wallet.balance < amount:
                raise serializers.ValidationError(
                    f'Недостаточно средств на счете. Доступно: {wallet.balance}'
                )
        return data

class RecurringOperationSerializer(serializers.ModelSerializer):
    """Сериализатор для повторяющихся операций"""
    base_operation = OperationSerializer(read_only=True)
    base_operation_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Будет установлено в __init__
        source='base_operation',
        write_only=True,
        required=True
    )

    class Meta:
        model = RecurringOperation
        fields = ['id', 'base_operation', 'base_operation_id', 'next_date', 'interval', 'is_active', 'end_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически устанавливаем queryset для base_operation_id
        user = self.context['request'].user if 'request' in self.context else None
        if user:
            self.fields['base_operation_id'].queryset = user.operations.all()

    def validate(self, data):
        """Валидация дат для повторяющейся операции"""
        if data.get('end_date') and data.get('next_date') and data['end_date'] <= data['next_date']:
            raise serializers.ValidationError(
                'Дата окончания должна быть позже даты начала'
            )
        return data
