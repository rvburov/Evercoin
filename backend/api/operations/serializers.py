# evercoin/backend/api/operations/serializers.py
from rest_framework import serializers
from .models import Operation
from api.wallets.models import Wallet
from api.categories.models import Category


class OperationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций с дополнительными данными о счете и категории
    """
    wallet_data = serializers.SerializerMethodField()
    category_data = serializers.SerializerMethodField()
    transfer_to_wallet_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Operation
        fields = [
            'id',
            'title',
            'amount',
            'description',
            'operation_type',
            'operation_date',
            'created_at',
            'updated_at',
            'wallet',
            'wallet_data',
            'category',
            'category_data',
            'transfer_to_wallet',
            'transfer_to_wallet_data'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def get_wallet_data(self, obj):
        """
        Получение данных о счете операции
        """
        if obj.wallet:
            return {
                'id': obj.wallet.id,
                'name': obj.wallet.name,
                'balance': obj.wallet.balance,
                'currency': obj.wallet.currency,
                'icon': obj.wallet.icon,
                'color': obj.wallet.color
            }
        return None
    
    def get_category_data(self, obj):
        """
        Получение данных о категории операции
        """
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'icon': obj.category.icon,
                'color': obj.category.color,
                'category_type': obj.category.category_type
            }
        return None
    
    def get_transfer_to_wallet_data(self, obj):
        """
        Получение данных о счете назначения для переводов
        """
        if obj.transfer_to_wallet:
            return {
                'id': obj.transfer_to_wallet.id,
                'name': obj.transfer_to_wallet.name,
                'balance': obj.transfer_to_wallet.balance,
                'currency': obj.transfer_to_wallet.currency,
                'icon': obj.transfer_to_wallet.icon,
                'color': obj.transfer_to_wallet.color
            }
        return None
    
    def validate(self, data):
        """
        Валидация данных операции
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        # Проверка владения счетом
        wallet = data.get('wallet')
        if wallet and wallet.user != user:
            raise serializers.ValidationError({'wallet': 'Вы не являетесь владельцем этого счета'})
        
        # Проверка владения категорией
        category = data.get('category')
        if category and category.user != user:
            raise serializers.ValidationError({'category': 'Вы не являетесь владельцем этой категории'})
        
        # Проверка счета назначения для переводов
        transfer_to_wallet = data.get('transfer_to_wallet')
        if data.get('operation_type') == 'transfer':
            if not transfer_to_wallet:
                raise serializers.ValidationError({'transfer_to_wallet': 'Для перевода необходимо указать счет назначения'})
            if transfer_to_wallet.user != user:
                raise serializers.ValidationError({'transfer_to_wallet': 'Вы не являетесь владельцем счета назначения'})
            if wallet == transfer_to_wallet:
                raise serializers.ValidationError({'transfer_to_wallet': 'Нельзя переводить на тот же счет'})
        
        # Проверка баланса для расходов
        if (data.get('operation_type') == 'expense' and 
            wallet and 
            data.get('amount') > wallet.balance):
            raise serializers.ValidationError({'amount': 'На счету недостаточно средств'})
        
        return data


class OperationCreateSerializer(OperationSerializer):
    """
    Сериализатор для создания операций с дополнительной валидацией
    """
    
    def create(self, validated_data):
        """
        Создание операции с автоматическим назначением пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class OperationUpdateSerializer(OperationSerializer):
    """
    Сериализатор для обновления операций
    """
    
    def update(self, instance, validated_data):
        """
        Обновление операции с проверкой прав доступа
        """
        # Сохраняем старые данные для обновления баланса
        old_amount = instance.amount
        old_type = instance.operation_type
        old_wallet = instance.wallet
        
        # Обновляем операцию
        operation = super().update(instance, validated_data)
        
        return operation


class OperationListSerializer(OperationSerializer):
    """
    Упрощенный сериализатор для списка операций
    """
    class Meta(OperationSerializer.Meta):
        fields = [
            'id',
            'title',
            'amount',
            'operation_type',
            'operation_date',
            'wallet_data',
            'category_data'
        ]
