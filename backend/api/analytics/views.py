# evercoin/backend/api/analytics/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .models import CachedAnalytics
from .serializers import (
    AnalyticsPeriodSerializer,
    MonthlySummarySerializer,
    CategoryStatsSerializer,
    MonthlyTrendsSerializer,
    DailyStatsSerializer,
    WalletStatsSerializer,
    OperationJournalSerializer,
    ReportScheduleSerializer,
    AnalyticsOverviewSerializer
)
from api.operations.models import Operation
from api.wallets.models import Wallet
from api.categories.models import Category


class AnalyticsBaseView(generics.GenericAPIView):
    """
    Базовый класс для аналитических представлений
    """
    permission_classes = [IsAuthenticated]
    
    def get_user_operations_queryset(self, user, start_date, end_date, wallet_ids=None):
        """
        Базовый queryset для операций пользователя с фильтрацией
        """
        queryset = Operation.objects.filter(
            user=user,
            operation_date__date__range=[start_date, end_date]
        ).select_related('wallet', 'category')
        
        if wallet_ids:
            queryset = queryset.filter(wallet_id__in=wallet_ids)
        
        return queryset
    
    def get_period_parameters(self, request):
        """
        Получение параметров периода из запроса
        """
        serializer = AnalyticsPeriodSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer


class MonthlySummaryView(AnalyticsBaseView):
    """
    API endpoint для получения сводки за месяц
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение сводки за месяц: доходы, расходы, категории
        """
        period_serializer = self.get_period_parameters(request)
        start_date, end_date = period_serializer.get_date_range()
        
        # Проверяем кеш
        cached_data = CachedAnalytics.get_cached_data(
            request.user, 
            'monthly_summary', 
            start_date, 
            end_date
        )
        
        if cached_data:
            return Response(cached_data)
        
        # Получаем операции за период
        operations = self.get_user_operations_queryset(
            request.user, start_date, end_date,
            period_serializer.validated_data.get('wallet_ids')
        )
        
        # Общие суммы
        total_income = operations.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_expense = operations.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        net_flow = total_income - total_expense
        
        # Категории доходов
        income_categories = (
            operations.filter(operation_type='income', category__isnull=False)
            .values('category__id', 'category__name', 'category__icon', 'category__color')
            .annotate(total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        
        # Категории расходов
        expense_categories = (
            operations.filter(operation_type='expense', category__isnull=False)
            .values('category__id', 'category__name', 'category__icon', 'category__color')
            .annotate(total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        
        # Форматируем данные
        income_categories_data = [
            {
                'category_id': item['category__id'],
                'category_name': item['category__name'],
                'category_icon': item['category__icon'],
                'category_color': item['category__color'],
                'total_amount': item['total_amount']
            }
            for item in income_categories
        ]
        
        expense_categories_data = [
            {
                'category_id': item['category__id'],
                'category_name': item['category__name'],
                'category_icon': item['category__icon'],
                'category_color': item['category__color'],
                'total_amount': item['total_amount']
            }
            for item in expense_categories
        ]
        
        result = {
            'period': f"{start_date.strftime('%Y-%m')}",
            'total_income': total_income,
            'total_expense': total_expense,
            'net_flow': net_flow,
            'income_categories': income_categories_data,
            'expense_categories': expense_categories_data
        }
        
        # Кешируем результат
        CachedAnalytics.set_cached_data(
            request.user, 
            'monthly_summary', 
            start_date, 
            end_date, 
            result
        )
        
        serializer = MonthlySummarySerializer(result)
        return Response(serializer.data)


class MonthlyTrendsView(AnalyticsBaseView):
    """
    API endpoint для получения трендов за 6 месяцев
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение финансовых трендов за последние 6 месяцев
        """
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=5)
        start_date = start_date.replace(day=1)
        
        # Проверяем кеш
        cached_data = CachedAnalytics.get_cached_data(
            request.user, 
            'monthly_trends', 
            start_date, 
            end_date
        )
        
        if cached_data:
            return Response(cached_data)
        
        trends_data = []
        current_date = start_date
        
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            next_month = month_start + relativedelta(months=1)
            month_end = next_month - timedelta(days=1)
            
            # Получаем операции за месяц
            operations = Operation.objects.filter(
                user=request.user,
                operation_date__date__range=[month_start, month_end]
            )
            
            income = operations.filter(operation_type='income').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            expense = operations.filter(operation_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            net_flow = income - expense
            
            trends_data.append({
                'period': month_start.strftime('%Y-%m'),
                'income': income,
                'expense': expense,
                'net_flow': net_flow
            })
            
            current_date = next_month
        
        # Кешируем результат
        CachedAnalytics.set_cached_data(
            request.user, 
            'monthly_trends', 
            start_date, 
            end_date, 
            trends_data
        )
        
        serializer = MonthlyTrendsSerializer(trends_data, many=True)
        return Response(serializer.data)


class CategoryAnalyticsView(AnalyticsBaseView):
    """
    API endpoint для детальной аналитики по категориям
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение детальной статистики по категориям
        """
        period_serializer = self.get_period_parameters(request)
        start_date, end_date = period_serializer.get_date_range()
        category_type = period_serializer.validated_data.get('category_type', 'all')
        
        # Проверяем кеш
        cache_key = f"category_stats_{category_type}"
        cached_data = CachedAnalytics.get_cached_data(
            request.user, 
            cache_key, 
            start_date, 
            end_date
        )
        
        if cached_data:
            return Response(cached_data)
        
        # Получаем операции за период
        operations = self.get_user_operations_queryset(
            request.user, start_date, end_date,
            period_serializer.validated_data.get('wallet_ids')
        )
        
        # Фильтруем по типу категории
        if category_type != 'all':
            operations = operations.filter(operation_type=category_type)
        
        # Группируем по категориям
        category_stats = (
            operations.filter(category__isnull=False)
            .values(
                'category__id', 
                'category__name', 
                'category__icon', 
                'category__color',
                'category__category_type'
            )
            .annotate(
                total_amount=Sum('amount'),
                operation_count=Count('id')
            )
            .order_by('-total_amount')
        )
        
        # Общая сумма для расчета процентов
        total_amount = sum(item['total_amount'] for item in category_stats)
        
        # Форматируем данные
        result = []
        for item in category_stats:
            percentage = (item['total_amount'] / total_amount * 100) if total_amount > 0 else 0
            
            result.append({
                'category_id': item['category__id'],
                'category_name': item['category__name'],
                'category_icon': item['category__icon'],
                'category_color': item['category__color'],
                'category_type': item['category__category_type'],
                'total_amount': item['total_amount'],
                'operation_count': item['operation_count'],
                'percentage': round(percentage, 2)
            })
        
        # Кешируем результат
        CachedAnalytics.set_cached_data(
            request.user, 
            cache_key, 
            start_date, 
            end_date, 
            result
        )
        
        serializer = CategoryStatsSerializer(result, many=True)
        return Response(serializer.data)


class DailyStatsView(AnalyticsBaseView):
    """
    API endpoint для дневной статистики
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение дневной статистики за период
        """
        period_serializer = self.get_period_parameters(request)
        start_date, end_date = period_serializer.get_date_range()
        
        # Ограничиваем период 90 днями для производительности
        if (end_date - start_date).days > 90:
            start_date = end_date - timedelta(days=90)
        
        # Проверяем кеш
        cached_data = CachedAnalytics.get_cached_data(
            request.user, 
            'daily_stats', 
            start_date, 
            end_date
        )
        
        if cached_data:
            return Response(cached_data)
        
        # Получаем ежедневную статистику
        daily_stats = (
            Operation.objects.filter(
                user=request.user,
                operation_date__date__range=[start_date, end_date]
            )
            .extra({'date': "date(operation_date)"})
            .values('date')
            .annotate(
                income=Sum('amount', filter=Q(operation_type='income')),
                expense=Sum('amount', filter=Q(operation_type='expense'))
            )
            .order_by('date')
        )
        
        # Форматируем данные
        result = []
        for day in daily_stats:
            income = day['income'] or 0
            expense = day['expense'] or 0
            net_flow = income - expense
            
            result.append({
                'date': day['date'],
                'income': income,
                'expense': expense,
                'net_flow': net_flow
            })
        
        # Кешируем результат
        CachedAnalytics.set_cached_data(
            request.user, 
            'daily_stats', 
            start_date, 
            end_date, 
            result
        )
        
        serializer = DailyStatsSerializer(result, many=True)
        return Response(serializer.data)


class WalletAnalyticsView(AnalyticsBaseView):
    """
    API endpoint для аналитики по счетам
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение статистики по всем счетам
        """
        period_serializer = self.get_period_parameters(request)
        start_date, end_date = period_serializer.get_date_range()
        
        # Проверяем кеш
        cached_data = CachedAnalytics.get_cached_data(
            request.user, 
            'wallet_stats', 
            start_date, 
            end_date
        )
        
        if cached_data:
            return Response(cached_data)
        
        # Получаем все счета пользователя
        wallets = Wallet.objects.filter(user=request.user, is_active=True)
        
        wallet_stats = []
        for wallet in wallets:
            # Операции по счету за период
            operations = Operation.objects.filter(
                user=request.user,
                wallet=wallet,
                operation_date__date__range=[start_date, end_date]
            )
            
            income = operations.filter(operation_type='income').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            expense = operations.filter(operation_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            net_flow = income - expense
            operation_count = operations.count()
            
            wallet_stats.append({
                'wallet_id': wallet.id,
                'wallet_name': wallet.name,
                'wallet_currency': wallet.currency,
                'wallet_icon': wallet.icon,
                'wallet_color': wallet.color,
                'balance': wallet.balance,
                'income': income,
                'expense': expense,
                'net_flow': net_flow,
                'operation_count': operation_count
            })
        
        # Сортируем по количеству операций
        wallet_stats.sort(key=lambda x: x['operation_count'], reverse=True)
        
        # Кешируем результат
        CachedAnalytics.set_cached_data(
            request.user, 
            'wallet_stats', 
            start_date, 
            end_date, 
            wallet_stats
        )
        
        serializer = WalletStatsSerializer(wallet_stats, many=True)
        return Response(serializer.data)


class OperationJournalView(AnalyticsBaseView):
    """
    API endpoint для журнала операций с фильтрацией
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение журнала операций с фильтрацией и пагинацией
        """
        period_serializer = self.get_period_parameters(request)
        start_date, end_date = period_serializer.get_date_range()
        
        # Получаем операции с фильтрацией
        operations = self.get_user_operations_queryset(
            request.user, start_date, end_date,
            period_serializer.validated_data.get('wallet_ids')
        )
        
        # Фильтрация по типу операции
        category_type = period_serializer.validated_data.get('category_type')
        if category_type and category_type != 'all':
            operations = operations.filter(operation_type=category_type)
        
        # Пагинация
        limit = min(int(request.query_params.get('limit', 100)), 500)  # Максимум 500 записей
        offset = int(request.query_params.get('offset', 0))
        
        operations = operations.order_by('-operation_date')[offset:offset + limit]
        
        # Форматируем данные
        result = []
        for operation in operations:
            result.append({
                'operation_id': operation.id,
                'title': operation.title,
                'amount': operation.amount,
                'operation_type': operation.operation_type,
                'operation_date': operation.operation_date,
                'wallet_name': operation.wallet.name,
                'wallet_currency': operation.wallet.currency,
                'category_name': operation.category.name if operation.category else None,
                'category_icon': operation.category.icon if operation.category else None,
                'category_color': operation.category.color if operation.category else None,
            })
        
        serializer = OperationJournalSerializer(result, many=True)
        return Response({
            'operations': serializer.data,
            'total_count': operations.count(),
            'limit': limit,
            'offset': offset
        })


class AnalyticsOverviewView(AnalyticsBaseView):
    """
    API endpoint для общего обзора аналитики
    """
    
    def get(self, request, *args, **kwargs):
        """
        Получение общего обзора финансовых показателей
        """
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        previous_month_start = (current_month_start - relativedelta(months=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        
        # Текущий месяц
        current_month_ops = Operation.objects.filter(
            user=request.user,
            operation_date__date__range=[current_month_start, today]
        )
        
        current_month_income = current_month_ops.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        current_month_expense = current_month_ops.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        current_month_net_flow = current_month_income - current_month_expense
        
        # Предыдущий месяц
        previous_month_ops = Operation.objects.filter(
            user=request.user,
            operation_date__date__range=[previous_month_start, previous_month_end]
        )
        
        previous_month_income = previous_month_ops.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        previous_month_expense = previous_month_ops.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        previous_month_net_flow = previous_month_income - previous_month_expense
        
        # Процентные изменения
        income_change_percentage = self._calculate_percentage_change(
            previous_month_income, current_month_income
        )
        expense_change_percentage = self._calculate_percentage_change(
            previous_month_expense, current_month_expense
        )
        
        # Общая статистика
        total_balance = Wallet.objects.filter(
            user=request.user, 
            is_hidden=False
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        active_wallets_count = Wallet.objects.filter(
            user=request.user, 
            is_active=True
        ).count()
        
        total_operations_count = Operation.objects.filter(user=request.user).count()
        
        result = {
            'current_month_income': current_month_income,
            'current_month_expense': current_month_expense,
            'current_month_net_flow': current_month_net_flow,
            'previous_month_income': previous_month_income,
            'previous_month_expense': previous_month_expense,
            'previous_month_net_flow': previous_month_net_flow,
            'income_change_percentage': income_change_percentage,
            'expense_change_percentage': expense_change_percentage,
            'total_balance': total_balance,
            'active_wallets_count': active_wallets_count,
            'total_operations_count': total_operations_count
        }
        
        serializer = AnalyticsOverviewSerializer(result)
        return Response(serializer.data)
    
    def _calculate_percentage_change(self, old_value, new_value):
        """
        Расчет процентного изменения
        """
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        
        return ((new_value - old_value) / old_value) * 100


@api_view(['POST'])
def clear_analytics_cache(request):
    """
    API endpoint для очистки кеша аналитики
    """
    try:
        deleted_count, _ = CachedAnalytics.objects.filter(user=request.user).delete()
        
        return Response({
            'message': f'Кеш аналитики очищен',
            'deleted_records': deleted_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Ошибка при очистке кеша: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )