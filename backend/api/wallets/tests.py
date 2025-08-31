# evercoin/backend/api/wallets/tests.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.wallets.models import Wallet, WalletTransfer

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def create_user():
    """Фикстура для создания пользователя."""
    def _create_user(email='test@example.com', username='testuser', password='TestPassword123!'):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
    return _create_user


@pytest.fixture
def authenticated_user(api_client, create_user):
    """Фикстура для аутентифицированного пользователя."""
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return user


@pytest.fixture
def wallet_data():
    """Фикстура с данными кошелька для тестов."""
    return {
        'name': 'Основной счет',
        'balance': 1000.00,
        'icon': 'wallet',
        'color': '#3B82F6',
        'currency': 'RUB',
        'is_default': True,
        'exclude_from_total': False,
    }


@pytest.fixture
def create_wallet(authenticated_user):
    """Фикстура для создания кошелька."""
    def _create_wallet(name='Основной счет', balance=1000.00, **kwargs):
        return Wallet.objects.create(
            user=authenticated_user,
            name=name,
            balance=balance,
            **kwargs
        )
    return _create_wallet


@pytest.fixture
def transfer_data(create_wallet):
    """Фикстура с данными перевода для тестов."""
    wallet1 = create_wallet(name='Кошелек 1', balance=2000.00)
    wallet2 = create_wallet(name='Кошелек 2', balance=500.00)
    
    return {
        'from_wallet': wallet1.id,
        'to_wallet': wallet2.id,
        'amount': 500.00,
        'description': 'Тестовый перевод',
    }


@pytest.mark.django_db
class TestWalletViewSet:
    """Тесты для ViewSet кошельков."""

    def test_create_wallet_success(self, api_client, authenticated_user, wallet_data):
        """Тест успешного создания кошелька."""
        url = reverse('wallet-list')
        response = api_client.post(url, wallet_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Wallet.objects.filter(user=authenticated_user, name=wallet_data['name']).exists()
        assert response.data['name'] == wallet_data['name']
        assert response.data['balance'] == str(wallet_data['balance'])

    def test_create_wallet_duplicate_name(self, api_client, authenticated_user, wallet_data, create_wallet):
        """Тест создания кошелька с уже существующим именем."""
        create_wallet(name=wallet_data['name'])
        
        url = reverse('wallet-list')
        response = api_client.post(url, wallet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_create_wallet_negative_balance(self, api_client, authenticated_user, wallet_data):
        """Тест создания кошелька с отрицательным балансом."""
        wallet_data['balance'] = -100.00
        
        url = reverse('wallet-list')
        response = api_client.post(url, wallet_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'balance' in response.data

    def test_list_wallets(self, api_client, authenticated_user, create_wallet):
        """Тест получения списка кошельков."""
        create_wallet(name='Кошелек 1')
        create_wallet(name='Кошелек 2')
        
        url = reverse('wallet-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_wallet(self, api_client, authenticated_user, create_wallet):
        """Тест получения детальной информации о кошельке."""
        wallet = create_wallet()
        
        url = reverse('wallet-detail', kwargs={'pk': wallet.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == wallet.id
        assert response.data['name'] == wallet.name

    def test_update_wallet(self, api_client, authenticated_user, create_wallet):
        """Тест обновления кошелька."""
        wallet = create_wallet()
        
        url = reverse('wallet-detail', kwargs={'pk': wallet.pk})
        update_data = {'name': 'Обновленное название'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        wallet.refresh_from_db()
        assert wallet.name == 'Обновленное название'

    def test_delete_wallet(self, api_client, authenticated_user, create_wallet):
        """Тест удаления кошелька."""
        wallet = create_wallet()
        
        url = reverse('wallet-detail', kwargs={'pk': wallet.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Wallet.objects.filter(id=wallet.id).exists()

    def test_wallet_summary(self, api_client, authenticated_user, create_wallet):
        """Тест получения сводной информации по кошелькам."""
        create_wallet(name='Кошелек 1', balance=1000.00)
        create_wallet(name='Кошелек 2', balance=500.00)
        create_wallet(name='Скрытый', balance=300.00, exclude_from_total=True)
        
        url = reverse('wallet-summary')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_balance'] == '1800.00'  # 1000 + 500 + 300
        assert response.data['visible_balance'] == '1500.00'  # 1000 + 500
        assert response.data['wallet_count'] == 3

    def test_set_default_wallet(self, api_client, authenticated_user, create_wallet):
        """Тест установки кошелька по умолчанию."""
        wallet1 = create_wallet(name='Кошелек 1', is_default=True)
        wallet2 = create_wallet(name='Кошелек 2', is_default=False)
        
        url = reverse('wallet-set-default', kwargs={'pk': wallet2.pk})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        
        assert not wallet1.is_default
        assert wallet2.is_default

    def test_update_balance(self, api_client, authenticated_user, create_wallet):
        """Тест ручного обновления баланса."""
        wallet = create_wallet(balance=1000.00)
        
        url = reverse('wallet-update-balance', kwargs={'pk': wallet.pk})
        update_data = {'balance': 1500.00}
        response = api_client.post(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        wallet.refresh_from_db()
        assert wallet.balance == 1500.00

    def test_update_balance_negative(self, api_client, authenticated_user, create_wallet):
        """Тест обновления баланса на отрицательное значение."""
        wallet = create_wallet()
        
        url = reverse('wallet-update-balance', kwargs={'pk': wallet.pk})
        update_data = {'balance': -100.00}
        response = api_client.post(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_wallet_operations(self, api_client, authenticated_user, create_wallet):
        """Тест получения операций по кошельку."""
        wallet = create_wallet()
        
        url = reverse('wallet-operations', kwargs={'pk': wallet.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data


@pytest.mark.django_db
class TestWalletTransferViewSet:
    """Тесты для ViewSet переводов между кошельками."""

    def test_create_transfer_success(self, api_client, authenticated_user, transfer_data):
        """Тест успешного создания перевода."""
        url = reverse('wallet-transfer-list')
        response = api_client.post(url, transfer_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert WalletTransfer.objects.filter(user=authenticated_user).exists()
        
        # Проверяем, что балансы обновились
        from_wallet = Wallet.objects.get(id=transfer_data['from_wallet'])
        to_wallet = Wallet.objects.get(id=transfer_data['to_wallet'])
        
        assert from_wallet.balance == 1500.00  # 2000 - 500
        assert to_wallet.balance == 1000.00    # 500 + 500

    def test_create_transfer_insufficient_funds(self, api_client, authenticated_user, transfer_data):
        """Тест создания перевода с недостаточными средствами."""
        transfer_data['amount'] = 3000.00  # Больше чем на счете
        
        url = reverse('wallet-transfer-list')
        response = api_client.post(url, transfer_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'На исходном счете недостаточно средств' in str(response.data)

    def test_create_transfer_same_wallet(self, api_client, authenticated_user, transfer_data):
        """Тест создания перевода на тот же кошелек."""
        transfer_data['to_wallet'] = transfer_data['from_wallet']
        
        url = reverse('wallet-transfer-list')
        response = api_client.post(url, transfer_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Нельзя переводить средства на тот же счет' in str(response.data)

    def test_list_transfers(self, api_client, authenticated_user, transfer_data):
        """Тест получения списка переводов."""
        # Создаем перевод
        url = reverse('wallet-transfer-list')
        api_client.post(url, transfer_data, format='json')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_transfer(self, api_client, authenticated_user, transfer_data):
        """Тест получения детальной информации о переводе."""
        # Создаем перевод
        url = reverse('wallet-transfer-list')
        create_response = api_client.post(url, transfer_data, format='json')
        transfer_id = create_response.data['id']
        
        url = reverse('wallet-transfer-detail', kwargs={'pk': transfer_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == transfer_id

    def test_recent_transfers(self, api_client, authenticated_user, transfer_data):
        """Тест получения последних переводов."""
        # Создаем несколько переводов
        url = reverse('wallet-transfer-list')
        for i in range(3):
            api_client.post(url, transfer_data, format='json')
        
        recent_url = reverse('wallet-transfer-recent-transfers')
        response = api_client.get(recent_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3


@pytest.mark.django_db
class TestWalletConstantsViewSet:
    """Тесты для ViewSet констант кошельков."""

    def test_get_icons(self, api_client, authenticated_user):
        """Тест получения списка иконок."""
        url = reverse('wallet-constants-icons')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0

    def test_get_colors(self, api_client, authenticated_user):
        """Тест получения списка цветов."""
        url = reverse('wallet-constants-colors')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0


@pytest.mark.django_db
class TestWalletModel:
    """Тесты для модели Wallet."""

    def test_wallet_creation(self, authenticated_user):
        """Тест создания кошелька."""
        wallet = Wallet.objects.create(
            user=authenticated_user,
            name='Тестовый кошелек',
            balance=1000.00,
            currency='RUB'
        )
        
        assert wallet is not None
        assert wallet.name == 'Тестовый кошелек'
        assert wallet.balance == 1000.00
        assert wallet.user == authenticated_user

    def test_wallet_str_representation(self, authenticated_user):
        """Тест строкового представления кошелька."""
        wallet = Wallet.objects.create(
            user=authenticated_user,
            name='Тестовый кошелек',
            balance=1000.00
        )
        
        expected_str = f"{authenticated_user.email} - Тестовый кошелек - 1000.00"
        assert str(wallet) == expected_str

    def test_set_default_wallet_behavior(self, authenticated_user):
        """Тест поведения при установке кошелька по умолчанию."""
        # Создаем несколько кошельков
        wallet1 = Wallet.objects.create(
            user=authenticated_user,
            name='Кошелек 1',
            balance=1000.00,
            is_default=True
        )
        
        wallet2 = Wallet.objects.create(
            user=authenticated_user,
            name='Кошелек 2',
            balance=2000.00,
            is_default=False
        )
        
        # Устанавливаем второй кошелек как основной
        wallet2.is_default = True
        wallet2.save()
        
        # Проверяем, что первый кошелек больше не основной
        wallet1.refresh_from_db()
        assert not wallet1.is_default
        assert wallet2.is_default


@pytest.mark.django_db
class TestWalletTransferModel:
    """Тесты для модели WalletTransfer."""

    def test_transfer_creation(self, authenticated_user, create_wallet):
        """Тест создания перевода."""
        from_wallet = create_wallet(name='Отправитель', balance=1000.00)
        to_wallet = create_wallet(name='Получатель', balance=500.00)
        
        transfer = WalletTransfer.objects.create(
            user=authenticated_user,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=300.00,
            description='Тестовый перевод'
        )
        
        assert transfer is not None
        assert transfer.amount == 300.00
        assert transfer.from_wallet == from_wallet
        assert transfer.to_wallet == to_wallet

    def test_transfer_str_representation(self, authenticated_user, create_wallet):
        """Тест строкового представления перевода."""
        from_wallet = create_wallet(name='Отправитель')
        to_wallet = create_wallet(name='Получатель')
        
        transfer = WalletTransfer.objects.create(
            user=authenticated_user,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=300.00
        )
        
        expected_str = f"Отправитель → Получатель - 300.00"
        assert str(transfer) == expected_str

    def test_transfer_updates_balances(self, authenticated_user, create_wallet):
        """Тест что перевод обновляет балансы кошельков."""
        from_wallet = create_wallet(name='Отправитель', balance=1000.00)
        to_wallet = create_wallet(name='Получатель', balance=500.00)
        
        transfer = WalletTransfer.objects.create(
            user=authenticated_user,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=300.00
        )
        
        # Проверяем обновленные балансы
        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()
        
        assert from_wallet.balance == 700.00  # 1000 - 300
        assert to_wallet.balance == 800.00    # 500 + 300


@pytest.mark.django_db
class TestAccessControl:
    """Тесты контроля доступа."""

    def test_anonymous_access_wallets(self, api_client):
        """Тест доступа анонимного пользователя к кошелькам."""
        url = reverse('wallet-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_access_transfers(self, api_client):
        """Тест доступа анонимного пользователя к переводам."""
        url = reverse('wallet-transfer-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_access_other_user_wallets(self, api_client, create_user):
        """Тест что пользователь не может видеть кошельки другого пользователя."""
        # Создаем двух пользователей
        user1 = create_user(email='user1@example.com')
        user2 = create_user(email='user2@example.com')
        
        # Создаем кошелек для второго пользователя
        wallet = Wallet.objects.create(
            user=user2,
            name='Чужой кошелек',
            balance=1000.00
        )
        
        # Аутентифицируем первого пользователя
        refresh = RefreshToken.for_user(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Пытаемся получить доступ к кошельку второго пользователя
        url = reverse('wallet-detail', kwargs={'pk': wallet.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestIntegration:
    """Интеграционные тесты полного рабочего процесса."""

    def test_complete_wallet_workflow(self, api_client, authenticated_user):
        """Тест полного рабочего процесса с кошельками."""
        # 1. Создаем кошелек
        wallet_data = {
            'name': 'Основной счет',
            'balance': 2000.00,
            'icon': 'wallet',
            'color': '#3B82F6',
            'currency': 'RUB',
            'is_default': True,
        }
        
        create_url = reverse('wallet-list')
        create_response = api_client.post(create_url, wallet_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        wallet_id = create_response.data['id']
        
        # 2. Получаем информацию о кошельке
        detail_url = reverse('wallet-detail', kwargs={'pk': wallet_id})
        detail_response = api_client.get(detail_url)
        assert detail_response.status_code == status.HTTP_200_OK
        
        # 3. Обновляем баланс
        update_balance_url = reverse('wallet-update-balance', kwargs={'pk': wallet_id})
        update_data = {'balance': 2500.00}
        update_response = api_client.post(update_balance_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        
        # 4. Получаем сводную информацию
        summary_url = reverse('wallet-summary')
        summary_response = api_client.get(summary_url)
        assert summary_response.status_code == status.HTTP_200_OK
        assert summary_response.data['total_balance'] == '2500.00'
        
        # 5. Создаем второй кошелек для перевода
        wallet2_data = {
            'name': 'Второй счет',
            'balance': 500.00,
            'icon': 'card',
            'color': '#10B981',
            'currency': 'RUB',
        }
        wallet2_response = api_client.post(create_url, wallet2_data, format='json')
        assert wallet2_response.status_code == status.HTTP_201_CREATED
        wallet2_id = wallet2_response.data['id']
        
        # 6. Создаем перевод между кошельками
        transfer_data = {
            'from_wallet': wallet_id,
            'to_wallet': wallet2_id,
            'amount': 1000.00,
            'description': 'Тестовый перевод',
        }
        transfer_url = reverse('wallet-transfer-list')
        transfer_response = api_client.post(transfer_url, transfer_data, format='json')
        assert transfer_response.status_code == status.HTTP_201_CREATED
        
        # 7. Проверяем обновленные балансы
        detail_response1 = api_client.get(detail_url)
        detail_response2 = api_client.get(reverse('wallet-detail', kwargs={'pk': wallet2_id}))
        
        assert detail_response1.data['balance'] == '1500.00'  # 2500 - 1000
        assert detail_response2.data['balance'] == '1500.00'  # 500 + 1000
        
        # 8. Удаляем кошелек
        delete_response = api_client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT