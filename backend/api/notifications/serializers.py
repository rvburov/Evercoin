# project/backend/api/notifications/serializers.py
from rest_framework import serializers
from .models import Notification
from django.utils import timezone
from operations.serializers import OperationSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для уведомлений с деталями связанной операции.
    Используется для отображения списка уведомлений.
    """
    operation = OperationSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'notification_date', 'is_read', 'operation',
            'created_at'
        ]
        read_only_fields = ['created_at', 'is_read']

class NotificationReadSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для пометки уведомлений как прочитанных.
    """
    class Meta:
        model = Notification
        fields = ['id', 'is_read']
        read_only_fields = ['id']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания уведомлений.
    Используется при создании уведомлений для повторяющихся операций.
    """
    class Meta:
        model = Notification
        fields = [
            'operation', 'notification_type',
            'title', 'message', 'notification_date'
        ]

    def validate_notification_date(self, value):
        """Проверка что дата уведомления не в прошлом"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Дата уведомления не может быть в прошлом"
            )
        return value
