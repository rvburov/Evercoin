# evercoin/backend/api/wallets/serializers.py
from rest_framework import serializers
from .models import Wallet, WalletTransfer
from api.operations.models import Operation

class WalletSerializer(serializers.ModelSerializer):
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    operation_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'name', 'balance', 'icon', 'color', 'is_default',
            'exclude_from_total', 'currency', 'created_at', 'updated_at',
            'total_balance', 'operation_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'balance']
    
    def validate_name(self, value):
        """Проверка уникальности названия счета для пользователя"""
        user = self.context['request'].user
        if self.instance:  # Редактирование существующего счета
            if Wallet.objects.filter(user=user, name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Счет с таким названием уже существует")
        else:  # Создание нового счета
            if Wallet.objects.filter(user=user, name=value).exists():
                raise serializers.ValidationError("Счет с таким названием уже существует")
        return value
    
    def validate_balance(self, value):
        """Проверка что баланс не отрицательный"""
        if value < 0:
            raise serializers.ValidationError("Баланс не может быть отрицательным")
        return value

class WalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['name', 'balance', 'icon', 'color', 'is_default', 'exclude_from_total', 'currency']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class WalletTransferSerializer(serializers.ModelSerializer):
    from_wallet_name = serializers.CharField(source='from_wallet.name', read_only=True)
    to_wallet_name = serializers.CharField(source='to_wallet.name', read_only=True)
    from_wallet_icon = serializers.CharField(source='from_wallet.icon', read_only=True)
    to_wallet_icon = serializers.CharField(source='to_wallet.icon', read_only=True)
    from_wallet_color = serializers.CharField(source='from_wallet.color', read_only=True)
    to_wallet_color = serializers.CharField(source='to_wallet.color', read_only=True)
    
    class Meta:
        model = WalletTransfer
        fields = [
            'id', 'from_wallet', 'to_wallet', 'amount', 'description',
            'from_wallet_name', 'to_wallet_name', 'from_wallet_icon',
            'to_wallet_icon', 'from_wallet_color', 'to_wallet_color',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        # Проверка что счета принадлежат пользователю
        user = self.context['request'].user
        from_wallet = data.get('from_wallet')
        to_wallet = data.get('to_wallet')
        
        if from_wallet.user != user or to_wallet.user != user:
            raise serializers.ValidationError("Счета должны принадлежать текущему пользователю")
        
        # Проверка что это разные счета
        if from_wallet == to_wallet:
            raise serializers.ValidationError("Нельзя переводить средства на тот же счет")
        
        # Проверка достаточности средств
        if from_wallet.balance < data.get('amount', 0):
            raise serializers.ValidationError("На исходном счете недостаточно средств")
        
        return data

class WalletSummarySerializer(serializers.Serializer):
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    visible_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    wallet_count = serializers.IntegerField()
    default_wallet = WalletSerializer()

class WalletOperationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    class Meta:
        model = Operation
        fields = [
            'id', 'amount', 'title', 'description', 'operation_type',
            'category', 'category_name', 'category_icon', 'category_color',
            'date', 'created_at'
        ]
