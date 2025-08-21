# project/backend/api/operations/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Operation
from .serializers import (
    OperationSerializer, 
    OperationCreateSerializer,
    OperationSummarySerializer,
    DailyOperationsSerializer,
    AnalyticsSerializer
)
from .pagination import OperationCursorPagination

class OperationViewSet(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    pagination_class = OperationCursorPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Operation.objects.filter(user=user).select_related(
            'wallet', 'category', 'transfer_to_wallet'
        )
        
        # Фильтрация по типу операции
        operation_type = self.request.query_params.get('type')
        if operation_type in ['income', 'expense', 'transfer']:
            queryset = queryset.filter(operation_type=operation_type)
        
        # Фильтрация по кошельку
        wallet_id = self.request.query_params.get('wallet')
        if wallet_id:
            queryset = queryset.filter(wallet_id=wallet_id)
        
        # Фильтрация по периоду
        period = self.request.query_params.get('period')
        if period:
            now = timezone.now()
            if period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__date=start_date.date())
            elif period == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
        
        # Фильтрация по конкретной дате
        date = self.request.query_params.get('date')
        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date=filter_date)
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OperationCreateSerializer
        return OperationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def income_summary(self, request):
        """Сводка по доходам за текущий месяц"""
        user = request.user
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Сумма по категориям доходов
        income_by_category = Operation.objects.filter(
            user=user,
            operation_type=Operation.INCOME,
            date__gte=start_of_month
        ).values(
            'category__name', 
            'category__icon', 
            'category__color'
        ).annotate(
            total_amount=Sum('amount'),
            operation_count=Count('id')
        ).order_by('-total_amount')
        
        # Общая сумма доходов
        total_income = Operation.objects.filter(
            user=user,
            operation_type=Operation.INCOME,
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        data = {
            'categories': OperationSummarySerializer(income_by_category, many=True).data,
            'total_income': total_income
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def expense_summary(self, request):
        """Сводка по расходам за текущий месяц"""
        user = request.user
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Сумма по категориям расходов
        expense_by_category = Operation.objects.filter(
            user=user,
            operation_type=Operation.EXPENSE,
            date__gte=start_of_month
        ).values(
            'category__name', 
            'category__icon', 
            'category__color'
        ).annotate(
            total_amount=Sum('amount'),
            operation_count=Count('id')
        ).order_by('-total_amount')
        
        # Общая сумма расходов
        total_expense = Operation.objects.filter(
            user=user,
            operation_type=Operation.EXPENSE,
            date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        data = {
            'categories': OperationSummarySerializer(expense_by_category, many=True).data,
            'total_expense': total_expense
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def daily_operations(self, request):
        """Операции с группировкой по дням"""
        user = request.user
        operations = self.get_queryset()
        
        # Группировка по дням
        daily_data = operations.extra(
            {'operation_date': "date(date)"}
        ).values('operation_date').annotate(
            total_amount=Sum('amount')
        ).order_by('-operation_date')
        
        # Получение операций для каждого дня
        result = []
        for day in daily_data:
            day_operations = operations.filter(
                date__date=day['operation_date']
            ).order_by('-date')
            
            result.append({
                'date': day['operation_date'],
                'total_amount': day['total_amount'],
                'operations': OperationSerializer(day_operations, many=True).data
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Аналитика операций"""
        user = request.user
        period = request.query_params.get('period', 'month')
        wallet_id = request.query_params.get('wallet')
        
        now = timezone.now()
        filters = {'user': user}
        
        if wallet_id:
            filters['wallet_id'] = wallet_id
        
        # Определение временного диапазона
        if period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Последний день месяца
            next_month = now.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=6)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            # По умолчанию - текущий год
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        filters['date__range'] = [start_date, end_date]
        
        # Расчет статистики
        income_operations = Operation.objects.filter(
            **filters, operation_type=Operation.INCOME
        )
        expense_operations = Operation.objects.filter(
            **filters, operation_type=Operation.EXPENSE
        )
        
        total_income = income_operations.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_expense = expense_operations.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_balance = total_income - total_expense
        
        data = {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'period': period,
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Дополнительная аналитика в зависимости от периода
        if period == 'year':
            # Среднемесячные значения
            months_passed = now.month
            data['average_monthly_income'] = total_income / months_passed if months_passed > 0 else Decimal('0')
            data['average_monthly_expense'] = total_expense / months_passed if months_passed > 0 else Decimal('0')
        
        elif period == 'month':
            # Недельная статистика
            weeks_passed = (now.day - 1) // 7 + 1
            data['weekly_income'] = total_income / weeks_passed if weeks_passed > 0 else Decimal('0')
            data['weekly_expense'] = total_expense / weeks_passed if weeks_passed > 0 else Decimal('0')
        
        elif period == 'week':
            # Дневная статистика
            days_passed = (now - start_date).days + 1
            data['daily_income'] = total_income / days_passed if days_passed > 0 else Decimal('0')
            data['daily_expense'] = total_expense / days_passed if days_passed > 0 else Decimal('0')
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def category_analytics(self, request):
        """Аналитика по категориям"""
        user = request.user
        period = request.query_params.get('period', 'month')
        wallet_id = request.query_params.get('wallet')
        operation_type = request.query_params.get('type')
        
        now = timezone.now()
        filters = {'user': user}
        
        if wallet_id:
            filters['wallet_id'] = wallet_id
        if operation_type in ['income', 'expense', 'transfer']:
            filters['operation_type'] = operation_type
        
        # Определение временного диапазона
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
        
        filters['date__gte'] = start_date
        
        # Статистика по категориям
        category_stats = Operation.objects.filter(
            **filters
        ).exclude(category__isnull=True).values(
            'category__id', 
            'category__name', 
            'category__icon', 
            'category__color',
            'category__operation_type'
        ).annotate(
            total_amount=Sum('amount'),
            operation_count=Count('id')
        ).order_by('-total_amount')
        
        # Общая статистика
        total_stats = Operation.objects.filter(**filters).aggregate(
            total_amount=Sum('amount'),
            total_count=Count('id')
        )
        
        data = {
            'categories': category_stats,
            'total_amount': total_stats['total_amount'] or Decimal('0'),
            'total_count': total_stats['total_count'] or 0,
            'period': period
        }
        
        return Response(data)
