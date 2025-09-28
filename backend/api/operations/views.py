# evercoin/backend/api/operations/views.py
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Operation
from .serializers import (
    OperationSerializer, 
    OperationCreateSerializer,
    OperationUpdateSerializer,
    OperationListSerializer
)
from .filters import OperationFilter


class OperationListView(generics.ListAPIView):
    """
    API endpoint для получения списка операций с пагинацией и фильтрацией
    """
    serializer_class = OperationListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OperationFilter
    ordering_fields = ['operation_date', 'amount', 'created_at']
    ordering = ['-operation_date']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        """
        Возвращает операции только текущего пользователя
        """
        return Operation.objects.filter(user=self.request.user).select_related(
            'wallet', 'category', 'transfer_to_wallet'
        )


class OperationDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей конкретной операции
    """
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает операции только текущего пользователя
        """
        return Operation.objects.filter(user=self.request.user).select_related(
            'wallet', 'category', 'transfer_to_wallet'
        )


class OperationCreateView(generics.CreateAPIView):
    """
    API endpoint для создания новой операции
    """
    serializer_class = OperationCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Создание операции с автоматическим назначением пользователя
        """
        serializer.save(user=self.request.user)


class OperationUpdateView(generics.UpdateAPIView):
    """
    API endpoint для обновления существующей операции
    """
    serializer_class = OperationUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает операции только текущего пользователя
        """
        return Operation.objects.filter(user=self.request.user)


class OperationDeleteView(generics.DestroyAPIView):
    """
    API endpoint для удаления операции
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает операции только текущего пользователя
        """
        return Operation.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        """
        Удаление операции с обновлением баланса счета
        """
        with transaction.atomic():
            instance.delete()


class OperationCopyView(generics.CreateAPIView):
    """
    API endpoint для копирования существующей операции
    """
    serializer_class = OperationCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Создание копии операции
        """
        try:
            original_operation = Operation.objects.get(
                pk=kwargs['pk'], 
                user=request.user
            )
            
            # Создаем копию операции
            operation_data = {
                'title': f"{original_operation.title} (копия)",
                'amount': original_operation.amount,
                'description': original_operation.description,
                'operation_type': original_operation.operation_type,
                'operation_date': timezone.now(),
                'wallet': original_operation.wallet,
                'category': original_operation.category,
                'transfer_to_wallet': original_operation.transfer_to_wallet,
            }
            
            serializer = self.get_serializer(data=operation_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Operation.DoesNotExist:
            return Response(
                {'error': 'Операция не найдена'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class OperationBulkDeleteView(generics.GenericAPIView):
    """
    API endpoint для массового удаления операций
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Массовое удаление операций
        """
        operation_ids = request.data.get('operation_ids', [])
        
        if not operation_ids:
            return Response(
                {'error': 'Не указаны ID операций для удаления'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            operations = Operation.objects.filter(
                id__in=operation_ids, 
                user=request.user
            )
            
            deleted_count, _ = operations.delete()
            
            return Response({
                'message': f'Удалено {deleted_count} операций',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Ошибка при удалении операций: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
