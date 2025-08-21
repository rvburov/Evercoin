# project/backend/api/categories/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Category
from .serializers import (
    CategorySerializer, 
    CategoryCreateSerializer,
    CategoryWithStatsSerializer
)
from core.constants.icons import CATEGORY_ICONS
from core.constants.colors import CATEGORY_COLORS

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(user=user)
        
        # Фильтрация по типу операции
        operation_type = self.request.query_params.get('type')
        if operation_type in ['income', 'expense']:
            queryset = queryset.filter(operation_type=operation_type)
        
        return queryset.order_by('operation_type', 'name')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def expense_categories(self, request):
        """Список всех категорий расходов"""
        categories = self.get_queryset().filter(operation_type=Category.EXPENSE)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def income_categories(self, request):
        """Список всех категорий доходов"""
        categories = self.get_queryset().filter(operation_type=Category.INCOME)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_icons(self, request):
        """Список доступных иконок"""
        return Response(CATEGORY_ICONS)
    
    @action(detail=False, methods=['get'])
    def available_colors(self, request):
        """Список доступных цветов"""
        return Response(CATEGORY_COLORS)
    
    @action(detail=False, methods=['get'])
    def with_stats(self, request):
        """Категории со статистикой операций"""
        user = request.user
        period = request.query_params.get('period', 'month')
        wallet_id = request.query_params.get('wallet')
        operation_type = request.query_params.get('type')
        
        # Базовый запрос
        categories = self.get_queryset()
        
        # Определение временного диапазона
        now = timezone.now()
        if period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # По умолчанию - текущий месяц
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Аннотация статистики
        categories = categories.annotate(
            operation_count=Count(
                'operations',
                filter=Q(
                    operations__date__gte=start_date,
                    **({'operations__wallet_id': wallet_id} if wallet_id else {})
                )
            ),
            total_amount=Sum(
                'operations__amount',
                filter=Q(
                    operations__date__gte=start_date,
                    **({'operations__wallet_id': wallet_id} if wallet_id else {})
                )
            )
        )
        
        # Фильтрация по типу операции если указан
        if operation_type in ['income', 'expense']:
            categories = categories.filter(operation_type=operation_type)
        
        serializer = CategoryWithStatsSerializer(categories, many=True)
        
        # Общая статистика
        from operations.models import Operation
        operation_filters = {
            'user': user,
            'date__gte': start_date,
            'category__isnull': False
        }
        
        if wallet_id:
            operation_filters['wallet_id'] = wallet_id
        if operation_type in ['income', 'expense']:
            operation_filters['operation_type'] = operation_type
        
        total_stats = Operation.objects.filter(**operation_filters).aggregate(
            total_amount=Sum('amount'),
            total_count=Count('id')
        )
        
        response_data = {
            'categories': serializer.data,
            'total_stats': {
                'total_amount': total_stats['total_amount'] or Decimal('0'),
                'total_count': total_stats['total_count'] or 0,
            },
            'period': period,
            'filter': {
                'wallet_id': wallet_id,
                'operation_type': operation_type
            }
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Статистика по конкретной категории"""
        category = self.get_object()
        period = request.query_params.get('period', 'month')
        wallet_id = request.query_params.get('wallet')
        
        # Определение временного диапазона
        now = timezone.now()
        if period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Фильтры для операций
        operation_filters = {
            'category': category,
            'date__gte': start_date
        }
        
        if wallet_id:
            operation_filters['wallet_id'] = wallet_id
        
        # Статистика операций
        operations = category.operations.filter(**operation_filters)
        stats = operations.aggregate(
            total_amount=Sum('amount'),
            operation_count=Count('id'),
            avg_amount=Avg('amount')
        )
        
        # Последние операции
        recent_operations = operations.order_by('-date')[:5]
        
        from operations.serializers import OperationSerializer
        recent_operations_data = OperationSerializer(recent_operations, many=True).data
        
        response_data = {
            'category': CategorySerializer(category).data,
            'statistics': {
                'total_amount': stats['total_amount'] or Decimal('0'),
                'operation_count': stats['operation_count'] or 0,
                'avg_amount': stats['avg_amount'] or Decimal('0'),
                'period': period
            },
            'recent_operations': recent_operations_data
        }
        
        return Response(response_data)
