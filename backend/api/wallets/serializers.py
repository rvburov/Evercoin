# evercoin/backend/api/wallets/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Wallet, WalletTransfer
from api.operations.models import Operation


class WalletSerializer(serializers.ModelSerializer):
    """
    Сериализатор для счетов с дополнительными вычисляемыми полями
    """
    total_income = serializers.ReadOnlyField()
    total_expense = serializers.ReadOnlyField()
    net_flow = serializers.ReadOnlyField()
    operation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = [
            'id',
            'name',
            'balance',
            'currency',
            'icon',
            'color',
            'is_default',
            'is_hidden',
            'description',
            'initial_balance',
            'total_income',
            'total_expense',
            'net_flow',
            'operation_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'balance', 'created_at', 'updated_at', 
            'total_income', 'total_expense', 'net_flow', 'operation_count'
        ]
    
    def get_operation_count(self, obj):
        """
        Получение количества операций по счету
        """
        return obj.operations.count()
    
    def validate(self, data):
        """
        Валидация данных счета
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        # Проверка уникальности названия счета для пользователя
        name = data.get('name')
        if name and user:
            existing_wallet = Wallet.objects.filter(user=user, name=name)
            if self.instance:  # При обновлении исключаем текущий счет
                existing_wallet = existing_wallet.exclude(pk=self.instance.pk)
            
            if existing_wallet.exists():
                raise serializers.ValidationError({
                    'name': 'У вас уже есть счет с таким названием'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Создание счета с автоматическим назначением пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        # Если это первый счет пользователя, делаем его счетом по умолчанию
        if not Wallet.objects.filter(user=validated_data['user']).exists():
            validated_data['is_default'] = True
        
        return super().create(validated_data)


class WalletCreateSerializer(WalletSerializer):
    """
    Сериализатор для создания счета с начальным балансом
    """
    
    def create(self, validated_data):
        """
        Создание счета с обработкой начального баланса
        """
        initial_balance = validated_data.get('initial_balance', 0)
        
        with transaction.atomic():
            wallet = super().create(validated_data)
            
            # Если указан начальный баланс, создаем операцию дохода
            if initial_balance != 0:
                Operation.objects.create(
                    user=wallet.user,
                    title=f"Начальный баланс счета {wallet.name}",
                    amount=initial_balance,
                    operation_type='income',
                    wallet=wallet,
                    description=f"Инициализация счета с начальным балансом {initial_balance} {wallet.currency}"
                )
        
        return wallet


class WalletUpdateSerializer(WalletSerializer):
    """
    Сериализатор для обновления счета
    """
    
    def update(self, instance, validated_data):
        """
        Обновление счета с проверкой прав доступа
        """
        # Сохраняем старое название для логирования
        old_name = instance.name
        
        wallet = super().update(instance, validated_data)
        
        # Если изменилось название, обновляем связанные операции
        if old_name != wallet.name:
            Operation.objects.filter(wallet=wallet).update(
                description=f"Операция по счету {wallet.name}"
            )
        
        return wallet


class WalletListSerializer(WalletSerializer):
    """
    Упрощенный сериализатор для списка счетов
    """
    class Meta(WalletSerializer.Meta):
        fields = [
            'id',
            'name',
            'balance',
            'currency',
            'icon',
            'color',
            'is_default',
            'is_hidden',
            'total_income',
            'total_expense',
            'net_flow',
            'operation_count'
        ]


class WalletTransferSerializer(serializers.ModelSerializer):
    """
    Сериализатор для переводов между счетами
    """
    from_wallet_data = serializers.SerializerMethodField()
    to_wallet_data = serializers.SerializerMethodField()
    
    class Meta:
        model = WalletTransfer
        fields = [
            'id',
            'from_wallet',
            'from_wallet_data',
            'to_wallet',
            'to_wallet_data',
            'amount',
            'description',
            'transfer_date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']
    
    def get_from_wallet_data(self, obj):
        """
        Получение данных о счете отправителя
        """
        return {
            'id': obj.from_wallet.id,
            'name': obj.from_wallet.name,
            'currency': obj.from_wallet.currency,
            'icon': obj.from_wallet.icon,
            'color': obj.from_wallet.color
        }
    
    def get_to_wallet_data(self, obj):
        """
        Получение данных о счете получателя
        """
        return {
            'id': obj.to_wallet.id,
            'name': obj.to_wallet.name,
            'currency': obj.to_wallet.currency,
            'icon': obj.to_wallet.icon,
            'color': obj.to_wallet.color
        }
    
    def validate(self, data):
        """
        Валидация данных перевода
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        from_wallet = data.get('from_wallet')
        to_wallet = data.get('to_wallet')
        amount = data.get('amount')
        
        # Проверка владения счетами
        if from_wallet and from_wallet.user != user:
            raise serializers.ValidationError({
                'from_wallet': 'Вы не являетесь владельцем счета отправителя'
            })
        
        if to_wallet and to_wallet.user != user:
            raise serializers.ValidationError({
                'to_wallet': 'Вы не являетесь владельцем счета получателя'
            })
        
        # Проверка, что счета разные
        if from_wallet and to_wallet and from_wallet == to_wallet:
            raise serializers.ValidationError({
                'to_wallet': 'Нельзя переводить средства на тот же счет'
            })
        
        # Проверка валюты счетов
        if from_wallet and to_wallet and from_wallet.currency != to_wallet.currency:
            raise serializers.ValidationError({
                'to_wallet': 'Переводы между счетами в разных валютах не поддерживаются'
            })
        
        # Проверка баланса счета отправителя
        if from_wallet and amount and amount > from_wallet.balance:
            raise serializers.ValidationError({
                'amount': 'На счете отправителя недостаточно средств'
            })
        
        return data
    
    def create(self, validated_data):
        """
        Создание перевода между счетами
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        with transaction.atomic():
            transfer = super().create(validated_data)
            
            # Создаем операции перевода
            Operation.objects.create(
                user=transfer.user,
                title=f"Перевод на {transfer.to_wallet.name}",
                amount=transfer.amount,
                description=transfer.description,
                operation_type='transfer',
                wallet=transfer.from_wallet,
                transfer_to_wallet=transfer.to_wallet,
                operation_date=transfer.transfer_date
            )
        
        return transfer


class WalletBalanceSerializer(serializers.Serializer):
    """
    Сериализатор для отображения общего баланса
    """
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    visible_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    hidden_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    wallet_count = serializers.IntegerField()
    currency = serializers.CharField()


class WalletDeleteSerializer(serializers.Serializer):
    """
    Сериализатор для обработки удаления счета
    """
    transfer_operations_to = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="ID счета для переноса операций"
    )
    delete_operations = serializers.BooleanField(
        default=False,
        help_text="Удалить все операции счета"
    )
    
    def validate_transfer_operations_to(self, value):
        """
        Валидация счета для переноса операций
        """
        if value:
            try:
                wallet = Wallet.objects.get(pk=value)
                request = self.context.get('request')
                if wallet.user != request.user:
                    raise serializers.ValidationError("Вы не являетесь владельцем этого счета")
            except Wallet.DoesNotExist:
                raise serializers.ValidationError("Счет не найден")
        return value