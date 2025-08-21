# project/backend/api/operations/serializers.py.py

from rest_framework import serializers
from .models import Operation
from wallets.serializers import WalletSerializer
from categories.serializers import CategorySerializer
from django.utils import timezone
from datetime import datetime, timedelta

class OperationSerializer(serializers.ModelSerializer):
    wallet_data = serializers.SerializerMethodField()
    category_data = serializers.SerializerMethodField()
    transfer_to_wallet_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Operation
        fields = [
            'id', 'amount', 'title', 'description', 'operation_type',
            'date', 'created_at', 'updated_at', 'wallet', 'category',
            'transfer_to_wallet', 'wallet_data', 'category_data',
            'transfer_to_wallet_data'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_wallet_data(self, obj):
        from wallets.serializers import WalletSerializer
        return WalletSerializer(obj.wallet).data
    
    def get_category_data(self, obj):
        if obj.category:
            from categories.serializers import CategorySerializer
            return CategorySerializer(obj.category).data
        return None
    
    def get_transfer_to_wallet_data(self, obj):
        if obj.transfer_to_wallet:
            from wallets.serializers import WalletSerializer
            return WalletSerializer(obj.transfer_to_wallet).data
        return None

class OperationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            'amount', 'title', 'description', 'operation_type',
            'date', 'wallet', 'category', 'transfer_to_wallet'
        ]
    
    def validate(self, data):
        operation_type = data.get('operation_type')
        wallet = data.get('wallet')
        amount = data.get('amount')
        transfer_to_wallet = data.get('transfer_to_wallet')
        
        # Проверка для расходов
        if operation_type == Operation.EXPENSE:
            if wallet.balance < amount:
                raise serializers.ValidationError({
                    'error': 'Недостаточно средств на счете',
                    'message': 'Невозможно добавить расход',
                    'logo': '/static/logo.png'
                })
        
        # Проверка для переводов
        if operation_type == Operation.TRANSFER:
            if not transfer_to_wallet:
                raise serializers.ValidationError('Для перевода необходимо указать целевой счет')
            if wallet == transfer_to_wallet:
                raise serializers.ValidationError('Нельзя переводить на тот же счет')
            if wallet.balance < amount:
                raise serializers.ValidationError({
                    'error': 'Недостаточно средств для перевода',
                    'message': 'Невозможно сделать перевод',
                    'logo': '/static/logo.png'
                })
        
        return data

class OperationSummarySerializer(serializers.Serializer):
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_name = serializers.CharField()
    category_icon = serializers.CharField()
    category_color = serializers.CharField()
    operation_count = serializers.IntegerField()

class DailyOperationsSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    operations = OperationSerializer(many=True)

class AnalyticsSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    average_monthly_expense = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    weekly_income = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    weekly_expense = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    daily_income = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    daily_expense = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
