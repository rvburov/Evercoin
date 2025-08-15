# backend/api/operations/views.py
from rest_framework import generics, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Operation, RecurringOperation
from .serializers import OperationSerializer, RecurringOperationSerializer
from .filters import OperationFilter
from .tasks import process_recurring_operations

class OperationListCreateView(generics.ListCreateAPIView):
    """Представление для списка и создания операций"""
    serializer_class = OperationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OperationFilter
    search_fields = ['name', 'description', 'amount']
    ordering_fields = ['date', 'amount']
    ordering = ['-date']

    def get_queryset(self):
        return Operation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для деталей, обновления и удаления операций"""
    serializer_class = OperationSerializer

    def get_queryset(self):
        return Operation.objects.filter(user=self.request.user)

class OperationSummaryView(generics.GenericAPIView):
    """Представление для сводной статистики по операциям"""
    filter_backends = [DjangoFilterBackend]
    filterset_class = OperationFilter

    def get_queryset(self):
        return Operation.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Пример агрегации данных
        total_income = queryset.filter(operation_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = queryset.filter(operation_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
        })

class RecurringOperationListCreateView(generics.ListCreateAPIView):
    """Представление для списка и создания повторяющихся операций"""
    serializer_class = RecurringOperationSerializer

    def get_queryset(self):
        return RecurringOperation.objects.filter(base_operation__user=self.request.user)

class RecurringOperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для деталей, обновления и удаления повторяющихся операций"""
    serializer_class = RecurringOperationSerializer

    def get_queryset(self):
        return RecurringOperation.objects.filter(base_operation__user=self.request.user)

class RecurringOperationProcessView(generics.GenericAPIView):
    """Представление для ручного запуска обработки повторяющихся операций"""
    
    def post(self, request, *args, **kwargs):
        process_recurring_operations.delay()
        return Response(
            {'status': 'started', 'message': 'Processing of recurring operations has been started'},
            status=status.HTTP_202_ACCEPTED
        )
