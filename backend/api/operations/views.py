from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Operation
from .serializers import (
    OperationSerializer, 
    OperationCreateSerializer,
    OperationAnalyticsSerializer,
    CategoryAnalyticsSerializer
)
from .filters import OperationFilter
from wallets.models import Wallet


class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OperationFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OperationCreateSerializer
        return OperationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related(
            'wallet', 'category'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        period = request.query_params.get('period', 'month')
        wallet_id = request.query_params.get('wallet')
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Date range calculation
        today = timezone.now().date()
        if period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        else:  # day
            start_date = end_date = today
            
        # Filter by date range
        queryset = queryset.filter(date__date__range=[start_date, end_date])
        
        # Analytics data
        analytics_data = {
            'total_income': queryset.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0,
            'total_expense': queryset.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0,
            'average_income': queryset.filter(type='income').aggregate(avg=Avg('amount'))['avg'] or 0,
            'average_expense': queryset.filter(type='expense').aggregate(avg=Avg('amount'))['avg'] or 0,
        }
        
        return Response(analytics_data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        category_stats = queryset.values(
            'category__id', 'category__name', 'category__color', 'category__icon'
        ).annotate(
            total_amount=Sum('amount'),
            operation_count=Count('id')
        ).filter(category__isnull=False)
        
        serializer = CategoryAnalyticsSerializer(
            [{
                'category': {
                    'id': stat['category__id'],
                    'name': stat['category__name'],
                    'color': stat['category__color'],
                    'icon': stat['category__icon'],
                },
                'total_amount': stat['total_amount'],
                'operation_count': stat['operation_count']
            } for stat in category_stats],
            many=True
        )
        
        return Response(serializer.data)

