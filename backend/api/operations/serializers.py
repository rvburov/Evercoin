# evercoin/backend/api/operations/serializers.py.py
from rest_framework import serializers
from .models import Operation, OperationLog
from api.categories.serializers import CategorySerializer
from api.wallets.serializers import WalletSerializer
from api.wallets.models import Wallet
from django.utils import timezone
from datetime import datetime, timedelta

class OperationSerializer(serializers.ModelSerializer):
    category_data = CategorySerializer(source='category', read_only=True)
    wallet_data = WalletSerializer(source='wallet', read_only=True)
    
    class Meta:
        model = Operation
        fields = [
            'id', 'amount', 'title', 'description', 'operation_type',
            'category', 'category_data', 'wallet', 'wallet_data',
            'date', 'created_at', 'updated_at', 'is_recurring', 'recurring_pattern'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Проверка баланса для расходных операций
        if data.get('operation_type') == 'expense' and data.get('wallet'):
            wallet = data['wallet']
            amount = data['amount']
            if wallet.balance < amount:
                raise serializers.ValidationError({
                    "detail": "На счету недостаточно средств",
                    "code": "insufficient_funds"
                })
        
        # Проверка отрицательных сумм
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError({
                "amount": "Сумма операции должна быть положительной"
            })
        
        # Проверка даты (не может быть в будущем)
        date = data.get('date')
        if date and date > timezone.now():
            raise serializers.ValidationError({
                "date": "Дата операции не может быть в будущем"
            })
        
        return data

class OperationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            'amount', 'title', 'description', 'operation_type',
            'category', 'wallet', 'date', 'is_recurring', 'recurring_pattern'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class OperationSummarySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    category_icon = serializers.CharField()
    category_color = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    operation_count = serializers.IntegerField()

class FinancialResultSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_result = serializers.DecimalField(max_digits=15, decimal_places=2)
    period = serializers.CharField()

class OperationFilterSerializer(serializers.Serializer):
    period = serializers.ChoiceField(
        choices=[('all', 'Все'), ('year', 'Год'), ('month', 'Месяц'), ('week', 'Неделя'), ('day', 'День')],
        default='all',
        required=False
    )
    wallet_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    operation_type = serializers.ChoiceField(
        choices=[('all', 'Все'), ('income', 'Доход'), ('expense', 'Расход'), ('transfer', 'Перевод')],
        default='all',
        required=False
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)

class OperationAnalyticsSerializer(serializers.Serializer):
    period = serializers.ChoiceField(
        choices=[('all', 'Все'), ('year', 'Год'), ('month', 'Месяц'), ('week', 'Неделя'), ('day', 'День')],
        default='all',
        required=False
    )
    wallet_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

class OperationLogSerializer(serializers.ModelSerializer):
    operation_title = serializers.CharField(source='operation.title', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'operation', 'operation_title', 'action',
            'old_data', 'new_data', 'created_at'
        ]
        read_only_fields = ['created_at']
