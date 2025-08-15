# project/backend/api/notifications/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Wallet
from .serializers import (
    WalletSerializer, 
    SimpleWalletSerializer,
    WalletTransferSerializer
)

class WalletListCreateView(generics.ListCreateAPIView):
    """
    Представление для получения списка счетов и создания нового счета.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только счета текущего пользователя"""
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании автоматически привязываем счет к пользователю"""
        serializer.save(user=self.request.user)

class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра, обновления и удаления счета.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ограничиваем доступ только к счетам текущего пользователя"""
        return Wallet.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """
        При удалении счета:
        1. Если это счет по умолчанию, назначаем новый
        2. Переносим операции на другой счет
        """
        user_wallets = Wallet.objects.filter(user=self.request.user).exclude(pk=instance.pk)
        
        if user_wallets.exists():
            # Находим новый счет по умолчанию
            new_default = user_wallets.filter(is_default=True).first()
            if not new_default:
                new_default = user_wallets.first()
                new_default.is_default = True
                new_default.save()
            
            # Переносим операции
            instance.operations.update(wallet=new_default)
        
        instance.delete()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer_funds(request):
    """
    Эндпоинт для перевода средств между счетами.
    Создает две операции: расход на одном счете и доход на другом.
    """
    serializer = WalletTransferSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    from_wallet = data['from_wallet']
    to_wallet = data['to_wallet']
    amount = data['amount']
    
    # Проверяем принадлежность счетов пользователю
    if (from_wallet.user != request.user or 
        to_wallet.user != request.user):
        return Response(
            {'detail': 'Недостаточно прав для операций с этими счетами'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Выполняем перевод
    from_wallet.balance -= amount
    to_wallet.balance += amount
    
    from_wallet.save()
    to_wallet.save()
    
    # Создаем записи операций (можно вынести в сигналы)
    from operations.models import Operation
    Operation.objects.create(
        user=request.user,
        name=f"Перевод на счет {to_wallet.name}",
        amount=amount,
        operation_type='expense',
        wallet=from_wallet,
        description=data.get('description', '')
    )
    Operation.objects.create(
        user=request.user,
        name=f"Перевод со счета {from_wallet.name}",
        amount=amount,
        operation_type='income',
        wallet=to_wallet,
        description=data.get('description', '')
    )
    
    return Response(
        {
            'message': 'Перевод выполнен успешно',
            'from_wallet': SimpleWalletSerializer(from_wallet).data,
            'to_wallet': SimpleWalletSerializer(to_wallet).data
        },
        status=status.HTTP_200_OK
    )
