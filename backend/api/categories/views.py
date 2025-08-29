# evercoin/backend/api/categories/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Category, CategoryBudget
from .serializers import (
    CategorySerializer, CategoryCreateSerializer, CategoryTreeSerializer,
    CategoryWithStatsSerializer, CategoryBudgetSerializer, CategoryAnalyticsSerializer
)
from api.operations.models import Operation

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).select_related('parent')
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return CategoryCreateSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Дерево категорий с иерархией"""
        categories = self.get_queryset().filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Категории по типу"""
        category_type = request.query_params.get('type')
        
        if category_type not in ['income', 'expense']:
            return Response(
                {"error": "Неверный тип категории. Допустимые значения: income, expense"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categories = self.get_queryset().filter(type=category_type, parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Аналитика по категориям"""
        serializer = CategoryAnalyticsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data
        
        # Фильтрация по периоду
        date_filter = self.get_date_filter(filters.get('period'))
        
        # Базовый queryset операций
        operations_queryset = Operation.objects.filter(user=request.user)
        
        if date_filter:
            operations_queryset = operations_queryset.filter(date__range=date_filter)
        
        # Фильтрация по счетам
        wallet_ids = filters.get('wallet_ids')
        if wallet_ids:
            operations_queryset = operations_queryset.filter(wallet_id__in=wallet_ids)
        
        # Фильтрация по типу категории
        category_type = filters.get('category_type')
        if category_type and category_type != 'all':
            operations_queryset = operations_queryset.filter(category__type=category_type)
        
        # Агрегация данных по категориям
        categories_data = Category.objects.filter(
            user=request.user,
            operations__in=operations_queryset
        ).annotate(
            total_amount=Sum('operations__amount'),
            operation_count=Count('operations')
        ).exclude(total_amount__isnull=True).order_by('-total_amount')
        
        # Общее количество операций и сумма
        total_operations = operations_queryset.count()
        total_amount = operations_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Расчет процентов
        category_stats = []
        for category in categories_data:
            percentage = (category.total_amount / total_amount * 100) if total_amount > 0 else 0
            category_stats.append({
                'id': category.id,
                'name': category.name,
                'type': category.type,
                'icon': category.icon,
                'color': category.color,
                'total_amount': category.total_amount,
                'operation_count': category.operation_count,
                'percentage': round(percentage, 2)
            })
        
        return Response({
            'categories': category_stats,
            'total_operations': total_operations,
            'total_amount': total_amount,
            'period': filters.get('period', 'all')
        })
    
    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """Операции по конкретной категории"""
        category = self.get_object()
        
        # Параметры фильтрации
        period = request.query_params.get('period', 'all')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        queryset = Operation.objects.filter(category=category)
        
        # Фильтрация по периоду
        if period != 'all':
            now = timezone.now()
            if period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
        
        # Пагинация
        total_count = queryset.count()
        operations = queryset.select_related('wallet').order_by('-date')[offset:offset + limit]
        
        from api.operations.serializers import OperationSerializer
        serializer = OperationSerializer(operations, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'next_offset': offset + limit if offset + limit < total_count else None,
            'previous_offset': offset - limit if offset > 0 else None
        })
    
    def get_date_filter(self, period):
        """Получение диапазона дат для фильтра по периоду"""
        now = timezone.now()
        
        if period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        else:
            return None
        
        return (start_date, end_date)

class CategoryBudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryBudgetSerializer
    
    def get_queryset(self):
        return CategoryBudget.objects.filter(user=self.request.user).select_related('category')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Активные бюджеты"""
        budgets = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Обзор бюджетов с прогрессом"""
        budgets = self.get_queryset().filter(is_active=True)
        
        budget_data = []
        for budget in budgets:
            budget_data.append({
                'id': budget.id,
                'category_id': budget.category.id,
                'category_name': budget.category.name,
                'category_icon': budget.category.icon,
                'category_color': budget.category.color,
                'budget_amount': budget.amount,
                'spent_amount': budget.spent_amount,
                'remaining_amount': budget.remaining_amount,
                'progress_percentage': budget.progress_percentage,
                'period': budget.period,
                'is_over_budget': budget.spent_amount > budget.amount
            })
        
        return Response(budget_data)

class CategoryConstantsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def icons(self, request):
        """Список доступных иконок для категорий"""
        from api.core.constants.icons import CATEGORY_ICONS
        return Response(CATEGORY_ICONS)
    
    @action(detail=False, methods=['get'])
    def colors(self, request):
        """Список доступных цветов для категорий"""
        from api.core.constants.colors import COLORS
        return Response(COLORS)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Типы категорий"""
        return Response([
            {'value': 'income', 'label': 'Доход'},
            {'value': 'expense', 'label': 'Расход'}
        ])
