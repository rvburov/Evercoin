# evercoin/backend/api/wallets/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db import transaction, models
from django.shortcuts import get_object_or_404

from .models import Wallet, WalletTransfer
from .serializers import (
    WalletSerializer,
    WalletCreateSerializer,
    WalletUpdateSerializer,
    WalletListSerializer,
    WalletTransferSerializer,
    WalletBalanceSerializer,
    WalletDeleteSerializer
)
from .filters import WalletFilter


class WalletListView(generics.ListAPIView):
    """
    API endpoint для получения списка счетов пользователя
    """
    serializer_class = WalletListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = WalletFilter
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['-is_default', '-created_at']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """
        Возвращает счета только текущего пользователя
        """
        return Wallet.objects.filter(user=self.request.user)


class WalletDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей конкретного счета
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает счета только текущего пользователя
        """
        return Wallet.objects.filter(user=self.request.user)


class WalletCreateView(generics.CreateAPIView):
    """
    API endpoint для создания нового счета
    """
    serializer_class = WalletCreateSerializer
    permission_classes = [IsAuthenticated]


class WalletUpdateView(generics.UpdateAPIView):
    """
    API endpoint для обновления существующего счета
    """
    serializer_class = WalletUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает счета только текущего пользователя
        """
        return Wallet.objects.filter(user=self.request.user)


class WalletDeleteView(generics.DestroyAPIView):
    """
    API endpoint для удаления счета с обработкой связанных операций
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает счета только текущего пользователя
        """
        return Wallet.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Обработка удаления счета с опциями переноса операций
        """
        wallet = self.get_object()
        serializer = WalletDeleteSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            return self._delete_wallet_with_options(wallet, serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _delete_wallet_with_options(self, wallet, options):
        """
        Удаление счета с выбранными опциями
        """
        from api.operations.models import Operation
        
        transfer_to_id = options.get('transfer_operations_to')
        delete_operations = options.get('delete_operations', False)
        
        try:
            with transaction.atomic():
                # Проверяем наличие операций
                operation_count = wallet.operations.count()
                transfer_operation_count = wallet.transfer_operations.count()
                total_operations = operation_count + transfer_operation_count
                
                if total_operations == 0:
                    # Если операций нет, просто удаляем счет
                    wallet.delete()
                    return Response(
                        {'message': 'Счет успешно удален'}, 
                        status=status.HTTP_200_OK
                    )
                
                if delete_operations:
                    # Удаляем все операции счета
                    wallet.operations.all().delete()
                    wallet.transfer_operations.all().delete()
                    wallet.delete()
                    return Response(
                        {'message': f'Счет и {total_operations} операций успешно удалены'}, 
                        status=status.HTTP_200_OK
                    )
                
                if transfer_to_id:
                    # Переносим операции на другой счет
                    transfer_to_wallet = Wallet.objects.get(pk=transfer_to_id, user=self.request.user)
                    
                    # Обновляем операции
                    Operation.objects.filter(wallet=wallet).update(wallet=transfer_to_wallet)
                    Operation.objects.filter(transfer_to_wallet=wallet).update(transfer_to_wallet=transfer_to_wallet)
                    
                    wallet.delete()
                    return Response(
                        {'message': f'Счет удален, операции перенесены на {transfer_to_wallet.name}'}, 
                        status=status.HTTP_200_OK
                    )
                
                # Если не выбрана опция, возвращаем ошибку
                return Response(
                    {
                        'error': 'Нельзя удалить счет с привязанными операциями',
                        'operation_count': total_operations,
                        'options': {
                            'transfer_operations_to': 'ID счета для переноса операций',
                            'delete_operations': 'Удалить все операции счета'
                        }
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Ошибка при удалении счета: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletTransferView(generics.CreateAPIView):
    """
    API endpoint для перевода средств между счетами
    """
    serializer_class = WalletTransferSerializer
    permission_classes = [IsAuthenticated]


class WalletBalanceView(generics.GenericAPIView):
    """
    API endpoint для получения общего баланса по всем счетам
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Получение общего баланса пользователя
        """
        wallets = Wallet.objects.filter(user=request.user)
        
        # Общий баланс всех счетов
        total_balance = wallets.aggregate(
            total=models.Sum('balance')
        )['total'] or 0
        
        # Баланс видимых счетов
        visible_balance = wallets.filter(is_hidden=False).aggregate(
            total=models.Sum('balance')
        )['total'] or 0
        
        # Баланс скрытых счетов
        hidden_balance = wallets.filter(is_hidden=True).aggregate(
            total=models.Sum('balance')
        )['total'] or 0
        
        # Основная валюта (валюта счета по умолчанию или первого счета)
        default_wallet = wallets.filter(is_default=True).first()
        if default_wallet:
            currency = default_wallet.currency
        elif wallets.exists():
            currency = wallets.first().currency
        else:
            currency = 'RUB'
        
        data = {
            'total_balance': total_balance,
            'visible_balance': visible_balance,
            'hidden_balance': hidden_balance,
            'wallet_count': wallets.count(),
            'currency': currency
        }
        
        serializer = WalletBalanceSerializer(data)
        return Response(serializer.data)


class WalletSetDefaultView(generics.GenericAPIView):
    """
    API endpoint для установки счета по умолчанию
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """
        Установка счета как счета по умолчанию
        """
        wallet = get_object_or_404(Wallet, pk=pk, user=request.user)
        
        with transaction.atomic():
            # Снимаем флаг default со всех счетов
            Wallet.objects.filter(user=request.user, is_default=True).update(is_default=False)
            # Устанавливаем флаг default для выбранного счета
            wallet.is_default = True
            wallet.save()
        
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class WalletHistoryView(generics.GenericAPIView):
    """
    API endpoint для получения истории баланса счета
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        """
        Получение истории баланса счета за указанный период
        """
        wallet = get_object_or_404(Wallet, pk=pk, user=request.user)
        
        # Получаем количество дней из параметра запроса
        days = int(request.query_params.get('days', 30))
        days = min(days, 365)  # Ограничиваем максимальный период
        
        history = wallet.get_balance_history(days=days)
        
        return Response({
            'wallet_id': wallet.id,
            'wallet_name': wallet.name,
            'period_days': days,
            'history': history
        })


@api_view(['GET'])
@transaction.atomic
def wallet_statistics(request):
    """
    API endpoint для получения статистики по всем счетам
    """
    wallets = Wallet.objects.filter(user=request.user)
    
    # Статистика по валютам
    currency_stats = (
        wallets.values('currency')
        .annotate(
            total_balance=models.Sum('balance'),
            wallet_count=models.Count('id'),
            visible_balance=models.Sum('balance', filter=models.Q(is_hidden=False)),
            hidden_balance=models.Sum('balance', filter=models.Q(is_hidden=True))
        )
        .order_by('-total_balance')
    )
    
    # Самые активные счета (по количеству операций)
    from api.operations.models import Operation
    active_wallets = (
        wallets.annotate(operation_count=models.Count('operations'))
        .order_by('-operation_count')[:5]
    )
    
    active_wallets_data = [
        {
            'id': wallet.id,
            'name': wallet.name,
            'operation_count': wallet.operation_count,
            'balance': wallet.balance,
            'currency': wallet.currency
        }
        for wallet in active_wallets
    ]
    
    return Response({
        'currency_statistics': list(currency_stats),
        'most_active_wallets': active_wallets_data,
        'total_wallets': wallets.count(),
        'default_currency': wallets.filter(is_default=True).first().currency if wallets.filter(is_default=True).exists() else 'RUB'
    })