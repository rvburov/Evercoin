# project/backend/api/notifications/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationReadSerializer,
    NotificationCreateSerializer
)

class NotificationListView(generics.ListAPIView):
    """
    Представление для получения списка непрочитанных уведомлений.
    Поддерживает пагинацию и фильтрацию по типу.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только актуальные непрочитанные уведомления пользователя"""
        queryset = Notification.objects.filter(
            user=self.request.user,
            is_read=False,
            notification_date__lte=timezone.now()
        ).select_related('operation', 'operation__category', 'operation__wallet')
        
        # Фильтрация по типу уведомления
        notification_type = self.request.query_params.get('type')
        if notification_type in dict(Notification.NOTIFICATION_TYPES).keys():
            queryset = queryset.filter(notification_type=notification_type)
            
        return queryset.order_by('-notification_date')

class NotificationMarkAsReadView(generics.UpdateAPIView):
    """
    Представление для пометки уведомления как прочитанного.
    Поддерживает массовое обновление.
    """
    serializer_class = NotificationReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        """Метод для массовой пометки уведомлений как прочитанных"""
        if 'all' in request.data and request.data['all']:
            updated = self.get_queryset().filter(is_read=False).update(is_read=True)
            return Response(
                {'status': f'{updated} уведомлений помечены как прочитанные'},
                status=status.HTTP_200_OK
            )
        return super().patch(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_upcoming_notification(request):
    """
    Эндпоинт для создания уведомлений о предстоящих операциях.
    Вызывается при создании операции с уведомлением.
    """
    serializer = NotificationCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Привязываем уведомление к пользователю операции
        operation = serializer.validated_data['operation']
        notification = serializer.save(
            user=operation.user,
            title=f"Скоро: {operation.name}",
            message=f"Сумма: {operation.amount} {operation.wallet.currency}"
        )
        
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
