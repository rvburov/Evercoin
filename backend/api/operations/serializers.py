from rest_framework import serializers
from .models import Operation
from wallets.serializers import WalletSerializer
from categories.serializers import CategorySerializer


class OperationSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Operation
        fields = [
            'id', 'title', 'amount', 'type', 'date', 
            'wallet', 'category', 'comment', 'is_repeat',
            'repeat_period', 'repeat_end_date', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class OperationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            'title', 'amount', 'type', 'date', 'wallet', 
            'category', 'comment', 'is_repeat', 'repeat_period',
            'repeat_end_date'
        ]
        
    def validate(self, data):
        if data['type'] == 'transfer' and 'category' in data and data['category'] is not None:
            raise serializers.ValidationError("Transfer operations cannot have a category")
        return data


class OperationAnalyticsSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    type = serializers.CharField()


class CategoryAnalyticsSerializer(serializers.Serializer):
    category = CategorySerializer()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    operation_count = serializers.IntegerField()
