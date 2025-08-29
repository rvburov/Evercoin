# evercoin/backend/api/operations/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from .models import Operation, OperationLog
from .serializers import (
    OperationSerializer, OperationCreateSerializer, 
    OperationSummarySerializer, FinancialResultSerializer,
    OperationFilterSerializer, OperationAnalyticsSerializer,
    OperationLogSerializer
)
from api.categories.models import Category
from api.wallets.models import Wallet

class OperationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationSerializer
    
    def get_queryset(self):
        return Operation.objects.filter(user=self.request.user).select_related(
            'category', 'wallet'
        ).prefetch_related('logs')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OperationCreateSerializer
        return OperationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            operation = self.perform_create(serializer)
            # Логирование создания операции
            OperationLog.objects.create(
                user=request.user,
                operation=operation,
                action='create',
                new_data=serializer.data
            )
        except ValueError as e:
            if str(e) == "На счету недостаточно средств":
                return Response({
                    "detail": "На счету недостаточно средств",
                    "code": "insufficient_funds"
                }, status=status.HTTP_400_BAD_REQUEST)
            raise
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Сохраняем старые данные для лога
        old_data = OperationSerializer(instance).data
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_update(serializer)
            # Логирование обновления операции
            OperationLog.objects.create(
                user=request.user,
                operation=instance,
                action='update',
                old_data=old_data,
                new_data=serializer.data
            )
        except ValueError as e:
            if str(e) == "На счету недостаточно средств":
                return Response({
                    "detail": "На счету недостаточно средств",
                    "code": "insufficient_funds"
                }, status=status.HTTP_400_BAD_REQUEST)
            raise
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Сохраняем данные для лога
        old_data = OperationSerializer(instance).data
        
        # Логирование удаления операции
        OperationLog.objects.create(
            user=request.user,
            operation=instance,
            action='delete',
            old_data=old_data
        )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def list_operations(self, request):
        """Список всех операций с пагинацией"""
        serializer = OperationFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data
        
        queryset = self.get_queryset()
        queryset = self.apply_filters(queryset, filters)
        
        # Курсорная пагинация
        limit = filters.get('limit', 20)
        offset = filters.get('offset', 0)
        
        operations = queryset[offset:offset + limit]
        serializer = self.get_serializer(operations, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'next_offset': offset + limit if offset + limit < queryset.count() else None,
            'previous_offset': offset - limit if offset > 0 else None
        })
    
    @action(detail=False, methods=['get'])
    def income_operations(self, request):
        """Операции по доходам за текущий месяц"""
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        # Категории доходов с суммами
        income_categories = Category.objects.filter(
            user=request.user, 
            type='income'
        ).annotate(
            total_amount=Sum('operations__amount', filter=Q(
                operations__operation_type='income',
                operations__date__gte=current_month,
                operations__date__lt=next_month
            )),
            operation_count=Count('operations', filter=Q(
                operations__operation_type='income',
                operations__date__gte=current_month,
                operations__date__lt=next_month
            ))
        )
        
        # Общая сумма доходов за месяц
        total_income = Operation.objects.filter(
            user=request.user,
            operation_type='income',
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_data = []
        for category in income_categories:
            if category.total_amount:
                category_data.append({
                    'category_name': category.name,
                    'category_icon': category.icon,
                    'category_color': category.color,
                    'total_amount': category.total_amount,
                    'operation_count': category.operation_count
                })
        
        return Response({
            'categories': category_data,
            'total_income': total_income,
            'period': current_month.strftime('%Y-%m')
        })
    
    @action(detail=False, methods=['get'])
    def expense_operations(self, request):
        """Операции по расходам за текущий месяц"""
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        # Категории расходов с суммами
        expense_categories = Category.objects.filter(
            user=request.user, 
            type='expense'
        ).annotate(
            total_amount=Sum('operations__amount', filter=Q(
                operations__operation_type='expense',
                operations__date__gte=current_month,
                operations__date__lt=next_month
            )),
            operation_count=Count('operations', filter=Q(
                operations__operation_type='expense',
                operations__date__gte=current_month,
                operations__date__lt=next_month
            ))
        )
        
        # Общая сумма расходов за месяц
        total_expense = Operation.objects.filter(
            user=request.user,
            operation_type='expense',
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_data = []
        for category in expense_categories:
            if category.total_amount:
                category_data.append({
                    'category_name': category.name,
                    'category_icon': category.icon,
                    'category_color': category.color,
                    'total_amount': category.total_amount,
                    'operation_count': category.operation_count
                })
        
        return Response({
            'categories': category_data,
            'total_expense': total_expense,
            'period': current_month.strftime('%Y-%m')
        })
    
    @action(detail=False, methods=['get'])
    def financial_analytics(self, request):
        """Аналитика доходов и расходов"""
        serializer = OperationAnalyticsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data
        
        # Фильтрация по периоду
        date_filter = self.get_date_filter(filters.get('period'))
        
        queryset = Operation.objects.filter(user=request.user)
        if date_filter:
            queryset = queryset.filter(date__range=date_filter)
        
        # Фильтрация по счетам
        wallet_ids = filters.get('wallet_ids')
        if wallet_ids:
            queryset = queryset.filter(wallet_id__in=wallet_ids)
        
        # Агрегация данных
        income = queryset.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expense = queryset.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        net_result = income - expense
        
        # Средние значения за прошедшие месяцы текущего года
        current_year = timezone.now().year
        year_operations = Operation.objects.filter(
            user=request.user,
            date__year=current_year,
            date__lt=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        )
        
        year_income = year_operations.filter(operation_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        year_expense = year_operations.filter(operation_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Количество прошедших месяцев в текущем году
        months_passed = timezone.now().month - 1
        if months_passed > 0:
            avg_income = year_income / months_passed
            avg_expense = year_expense / months_passed
        else:
            avg_income = avg_expense = 0
        
        # Финансовый результат по месяцам (последние 6 месяцев)
        monthly_results = []
        for i in range(6):
            month_date = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            month_income = Operation.objects.filter(
                user=request.user,
                operation_type='income',
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expense = Operation.objects.filter(
                user=request.user,
                operation_type='expense',
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_results.append({
                'month': month_start.strftime('%Y-%m'),
                'income': month_income,
                'expense': month_expense,
                'net_result': month_income - month_expense
            })
        
        return Response({
            'current_period': {
                'income': income,
                'expense': expense,
                'net_result': net_result
            },
            'averages': {
                'income': avg_income,
                'expense': avg_expense,
                'net_result': avg_income - avg_expense
            },
            'monthly_results': monthly_results,
            'period': filters.get('period', 'all')
        })
    
    @action(detail=False, methods=['get'])
    def daily_financial_result(self, request):
        """Финансовый результат за день"""
        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_date = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
                end_date = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))
            except ValueError:
                return Response(
                    {"error": "Неверный формат даты. Используйте YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # По умолчанию текущий день
            now = timezone.now()
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_income = Operation.objects.filter(
            user=request.user,
            operation_type='income',
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        daily_expense = Operation.objects.filter(
            user=request.user,
            operation_type='expense',
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'date': start_date.date().isoformat(),
            'income': daily_income,
            'expense': daily_expense,
            'net_result': daily_income - daily_expense
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Дублирование операции"""
        operation = self.get_object()
        
        # Создаем копию операции
        duplicate_operation = Operation.objects.create(
            user=operation.user,
            amount=operation.amount,
            title=f"{operation.title} (копия)",
            description=operation.description,
            operation_type=operation.operation_type,
            category=operation.category,
            wallet=operation.wallet,
            date=timezone.now(),
            is_recurring=operation.is_recurring,
            recurring_pattern=operation.recurring_pattern
        )
        
        # Логирование дублирования
        OperationLog.objects.create(
            user=request.user,
            operation=duplicate_operation,
            action='duplicate',
            old_data=OperationSerializer(operation).data
        )
        
        serializer = self.get_serializer(duplicate_operation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def apply_filters(self, queryset, filters):
        """Применение фильтров к queryset"""
        # Фильтрация по периоду
        date_filter = self.get_date_filter(filters.get('period'))
        if date_filter:
            queryset = queryset.filter(date__range=date_filter)
        
        # Фильтрация по счетам
        wallet_ids = filters.get('wallet_ids')
        if wallet_ids:
            queryset = queryset.filter(wallet_id__in=wallet_ids)
        
        # Фильтрация по типу операции
        operation_type = filters.get('operation_type')
        if operation_type and operation_type != 'all':
            queryset = queryset.filter(operation_type=operation_type)
        
        # Фильтрация по категориям
        category_ids = filters.get('category_ids')
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)
        
        # Фильтрация по дате (если указаны start_date/end_date)
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
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

class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OperationLogSerializer
    
    def get_queryset(self):
        return OperationLog.objects.filter(user=self.request.user).select_related('operation')
