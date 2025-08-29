# evercoin/backend/api/wallets/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Wallet, WalletTransfer
from .serializers import (
    WalletSerializer, WalletCreateSerializer, 
    WalletTransferSerializer, WalletSummarySerializer,
    WalletOperationSerializer
)
from api.operations.models import Operation

class WalletViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user).prefetch_related('operations')
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return WalletCreateSerializer
        return WalletSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Сводная информация по всем счетам"""
        wallets = self.get_queryset()
        
        # Общий баланс всех счетов
        total_balance = wallets.aggregate(total=Sum('balance'))['total'] or 0
        
        # Баланс только видимых счетов
        visible_balance = wallets.filter(exclude_from_total=False).aggregate(
            total=Sum('balance')
        )['total'] or 0
        
        # Счет по умолчанию
        default_wallet = wallets.filter(is_default=True).first()
        
        data = {
            'total_balance': total_balance,
            'visible_balance': visible_balance,
            'wallet_count': wallets.count(),
            'default_wallet': WalletSerializer(default_wallet).data if default_wallet else None
        }
        
        serializer = WalletSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """Операции по конкретному счету"""
        wallet = self.get_object()
        
        # Параметры фильтрации
        period = request.query_params.get('period', 'all')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        queryset = Operation.objects.filter(wallet=wallet)
        
        # Фильтрация по периоду
        if period != 'all':
            now = timezone.now()
            if period == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'week':
                start_date = now - timezone.timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
            elif period == 'day':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(date__gte=start_date)
        
        # Пагинация
        total_count = queryset.count()
        operations = queryset.select_related('category').order_by('-date')[offset:offset + limit]
        
        serializer = WalletOperationSerializer(operations, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'next_offset': offset + limit if offset + limit < total_count else None,
            'previous_offset': offset - limit if offset > 0 else None
        })
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Установка счета по умолчанию"""
        wallet = self.get_object()
        wallet.is_default = True
        wallet.save()
        
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_balance(self, request, pk=None):
        """Ручное обновление баланса счета"""
        wallet = self.get_object()
        new_balance = request.data.get('balance')
        
        if new_balance is None:
            return Response(
                {"error": "Параметр balance обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_balance = float(new_balance)
            if new_balance < 0:
                return Response(
                    {"error": "Баланс не может быть отрицательным"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Некорректное значение баланса"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wallet.balance = new_balance
        wallet.save()
        
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

class WalletTransferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletTransferSerializer
    
    def get_queryset(self):
        return WalletTransfer.objects.filter(user=self.request.user).select_related(
            'from_wallet', 'to_wallet'
        )
    
    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except ValueError as e:
            if str(e) == "На исходном счете недостаточно средств":
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"detail": "На исходном счете недостаточно средств"})
            raise
    
    @action(detail=False, methods=['get'])
    def recent_transfers(self, request):
        """Последние переводы между счетами"""
        limit = int(request.query_params.get('limit', 10))
        transfers = self.get_queryset().order_by('-created_at')[:limit]
        
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)

class WalletConstantsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def icons(self, request):
        """Список доступных иконок для счетов"""
        from api.core.constants.icons import WALLET_ICONS
        return Response(WALLET_ICONS)
    
    @action(detail=False, methods=['get'])
    def colors(self, request):
        """Список доступных цветов для счетов"""
        from api.core.constants.colors import COLORS
        return Response(COLORS)
