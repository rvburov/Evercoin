# evercoin/backend/api/operations/tests.py
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from api.operations.models import Operation, OperationLog
from api.categories.models import Category
from api.wallets.models import Wallet

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def create_user():
    """Фикстура для создания пользователя."""
    user_counter = 0
    
    def _create_user(email=None, username=None, password='TestPassword123!'):
        nonlocal user_counter
        user_counter += 1
        
        if email is None:
            email = f'test{user_counter}@example.com'
        if username is None:
            username = f'testuser{user_counter}'
        
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
def create_category():
    """Фикстура для создания категории."""
    category_counter = 0
    
    def _create_category(user, name=None, type='expense'):
        nonlocal category_counter
        category_counter += 1
        
        if name is None:
            name = f'Test Category {category_counter}'
        
        return Category.objects.create(
            name=name,
            type=type,
            user=user,
            icon='test-icon',
            color='#FFFFFF'
        )
    return _create_category


@pytest.fixture
def create_wallet():
    """Фикстура для создания кошелька."""
    wallet_counter = 0
    
    def _create_wallet(user, name=None, balance=1000.00):
        nonlocal wallet_counter
        wallet_counter += 1
        
        if name is None:
            name = f'Test Wallet {wallet_counter}'
        
        return Wallet.objects.create(
            name=name,
            balance=balance,
            currency='USD',
            user=user
        )
    return _create_wallet


@pytest.fixture
def create_operation(create_category, create_wallet):
    """Фикстура для создания операции."""
    operation_counter = 0
    
    def _create_operation(
        user,
        category=None,
        wallet=None,
        amount=100.00,
        title=None,
        operation_type='expense',
        date=None
    ):
        nonlocal operation_counter
        operation_counter += 1
        
        if category is None:
            category = create_category(user)
        if wallet is None:
            wallet = create_wallet(user)
        if title is None:
            title = f'Test Operation {operation_counter}'
        if date is None:
            date = timezone.now()
        
        return Operation.objects.create(
            user=user,
            category=category,
            wallet=wallet,
            amount=amount,
            title=title,
            operation_type=operation_type,
            date=date
        )
    return _create_operation


@pytest.fixture
def operation_data(authenticated_user, create_category, create_wallet):
    """Фикстура с данными операции для тестов."""
    category = create_category(authenticated_user)
    wallet = create_wallet(authenticated_user)
    
    return {
        'amount': '100.00',
        'title': 'Test Operation',
        'description': 'Test description',
        'operation_type': 'expense',
        'category': category.id,
        'wallet': wallet.id,
        'date': timezone.now().isoformat()
    }


@pytest.mark.django_db
class TestOperationViewSet:
    """Тесты для ViewSet операций."""

    def test_create_operation_success(self, api_client, authenticated_user, operation_data):
        """Тест успешного создания операции."""
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Operation.objects.filter(user=authenticated_user).exists()
        
        # Проверяем что лог создался
        operation = Operation.objects.get(user=authenticated_user)
        assert OperationLog.objects.filter(
            user=authenticated_user,
            operation=operation,
            action='create'
        ).exists()

    def test_create_operation_insufficient_funds(self, api_client, authenticated_user, create_wallet, create_category):
        """Тест создания операции с недостаточными средствами."""
        # Создаем кошелек с нулевым балансом
        wallet = create_wallet(authenticated_user, balance=0.00)
        category = create_category(authenticated_user)
        
        operation_data = {
            'amount': '100.00',
            'title': 'Test Operation',
            'operation_type': 'expense',
            'category': category.id,
            'wallet': wallet.id,
            'date': timezone.now().isoformat()
        }
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'insufficient_funds'

    def test_create_operation_negative_amount(self, api_client, authenticated_user, operation_data):
        """Тест создания операции с отрицательной суммой."""
        operation_data['amount'] = '-100.00'
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_operation_future_date(self, api_client, authenticated_user, operation_data):
        """Тест создания операции с датой в будущем."""
        future_date = timezone.now() + timedelta(days=1)
        operation_data['date'] = future_date.isoformat()
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_operations(self, api_client, authenticated_user, create_operation):
        """Тест получения списка операций."""
        # Создаем несколько операций
        create_operation(authenticated_user)
        create_operation(authenticated_user)
        
        url = reverse('operation-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_retrieve_operation(self, api_client, authenticated_user, create_operation):
        """Тест получения конкретной операции."""
        operation = create_operation(authenticated_user)
        
        url = reverse('operation-detail', kwargs={'pk': operation.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == operation.id

    def test_update_operation(self, api_client, authenticated_user, create_operation):
        """Тест обновления операции."""
        operation = create_operation(authenticated_user)
        
        url = reverse('operation-detail', kwargs={'pk': operation.pk})
        update_data = {'title': 'Updated Title'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        operation.refresh_from_db()
        assert operation.title == 'Updated Title'
        
        # Проверяем лог обновления
        assert OperationLog.objects.filter(
            user=authenticated_user,
            operation=operation,
            action='update'
        ).exists()

    def test_delete_operation(self, api_client, authenticated_user, create_operation):
        """Тест удаления операции."""
        operation = create_operation(authenticated_user)
        operation_id = operation.id
        
        url = reverse('operation-detail', kwargs={'pk': operation_id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Operation.objects.filter(id=operation_id).exists()
        
        # Проверяем лог удаления
        assert OperationLog.objects.filter(
            user=authenticated_user,
            operation_id=operation_id,
            action='delete'
        ).exists()

    def test_operation_access_other_user(self, api_client, create_user, create_operation):
        """Тест доступа к операции другого пользователя."""
        user1 = create_user()
        user2 = create_user()
        
        operation = create_operation(user1)
        
        # Аутентифицируем второго пользователя
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('operation-detail', kwargs={'pk': operation.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOperationCustomEndpoints:
    """Тесты для кастомных endpoints операций."""

    def test_list_operations_filtered(self, api_client, authenticated_user, create_operation):
        """Тест отфильтрованного списка операций."""
        # Создаем операции разных типов
        create_operation(authenticated_user, operation_type='expense')
        create_operation(authenticated_user, operation_type='income')
        
        url = reverse('operation-list-filtered')
        response = api_client.get(url, {'operation_type': 'expense'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['operation_type'] == 'expense'

    def test_income_operations(self, api_client, authenticated_user, create_operation, create_category):
        """Тест получения доходов по категориям."""
        category = create_category(authenticated_user, type='income', name='Income Category')
        create_operation(
            user=authenticated_user,
            category=category,
            operation_type='income',
            amount=200.00
        )
        
        url = reverse('operation-income')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_income']) == Decimal('200.00')
        assert len(response.data['categories']) == 1

    def test_expense_operations(self, api_client, authenticated_user, create_operation, create_category):
        """Тест получения расходов по категориям."""
        category = create_category(authenticated_user, type='expense', name='Expense Category')
        create_operation(
            user=authenticated_user,
            category=category,
            operation_type='expense',
            amount=150.00
        )
        
        url = reverse('operation-expense')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_expense']) == Decimal('150.00')
        assert len(response.data['categories']) == 1

    def test_financial_analytics(self, api_client, authenticated_user, create_operation):
        """Тест финансовой аналитики."""
        # Создаем доходы и расходы
        create_operation(
            authenticated_user,
            operation_type='income',
            amount=300.00
        )
        create_operation(
            authenticated_user,
            operation_type='expense',
            amount=100.00
        )
        
        url = reverse('operation-analytics-financial')
        response = api_client.get(url, {'period': 'month'})
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['current_period']['income']) == Decimal('300.00')
        assert Decimal(response.data['current_period']['expense']) == Decimal('100.00')
        assert Decimal(response.data['current_period']['net_result']) == Decimal('200.00')

    def test_daily_financial_result(self, api_client, authenticated_user, create_operation):
        """Тест ежедневного финансового результата."""
        today = timezone.now().date()
        
        create_operation(
            user=authenticated_user,
            operation_type='income',
            amount=500.00,
            date=timezone.make_aware(datetime.combine(today, datetime.min.time()))
        )
        create_operation(
            user=authenticated_user,
            operation_type='expense',
            amount=200.00,
            date=timezone.make_aware(datetime.combine(today, datetime.min.time()))
        )
        
        url = reverse('operation-daily-result')
        response = api_client.get(url, {'date': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['income']) == Decimal('500.00')
        assert Decimal(response.data['expense']) == Decimal('200.00')
        assert Decimal(response.data['net_result']) == Decimal('300.00')

    def test_duplicate_operation(self, api_client, authenticated_user, create_operation):
        """Тест дублирования операции."""
        operation = create_operation(authenticated_user)
        
        url = reverse('operation-detail', kwargs={'pk': operation.pk}) + 'duplicate/'
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Operation.objects.filter(user=authenticated_user).count() == 2
        
        # Проверяем лог дублирования
        assert OperationLog.objects.filter(
            user=authenticated_user,
            action='duplicate'
        ).exists()


@pytest.mark.django_db
class TestOperationLogViewSet:
    """Тесты для ViewSet логов операций."""

    def test_list_operation_logs(self, api_client, authenticated_user, create_operation):
        """Тест получения списка логов операций."""
        operation = create_operation(authenticated_user)
        
        url = reverse('operation-log-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1  # Как минимум лог создания

    def test_retrieve_operation_log(self, api_client, authenticated_user, create_operation):
        """Тест получения конкретного лога операции."""
        operation = create_operation(authenticated_user)
        log = OperationLog.objects.filter(operation=operation).first()
        assert log is not None
        
        url = reverse('operation-log-detail', kwargs={'pk': log.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == log.id

    def test_log_access_other_user(self, api_client, create_user, create_operation):
        """Тест доступа к логу другого пользователя."""
        user1 = create_user()
        user2 = create_user()
        
        operation = create_operation(user1)
        log = OperationLog.objects.filter(operation=operation).first()
        assert log is not None
        
        # Аутентифицируем второго пользователя
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('operation-log-detail', kwargs={'pk': log.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOperationModel:
    """Тесты для модели Operation."""

    def test_operation_creation(self, create_user, create_operation):
        """Тест создания операции."""
        user = create_user()
        operation = create_operation(user)
        assert operation is not None
        assert operation.user == user
        assert operation.amount == Decimal('100.00')

    def test_operation_string_representation(self, create_user, create_operation):
        """Тест строкового представления операции."""
        user = create_user()
        operation = create_operation(user, title='Test Operation')
        expected_str = f"{user.email} - Test Operation - 100.00"
        assert str(operation) == expected_str

    def test_operation_ordering(self, create_user, create_operation):
        """Тест порядка сортировки операций."""
        user = create_user()
        
        # Создаем операции с разными датами
        operation1 = create_operation(
            user,
            date=timezone.now() - timedelta(days=1)
        )
        operation2 = create_operation(
            user,
            date=timezone.now()
        )
        
        operations = Operation.objects.filter(user=user).order_by('-date', '-created_at')
        assert operations[0] == operation2  # Самая свежая операция первая
        assert operations[1] == operation1


@pytest.mark.django_db
class TestOperationLogModel:
    """Тесты для модели OperationLog."""

    def test_operation_log_creation(self, create_user, create_operation):
        """Тест создания лога операции."""
        user = create_user()
        operation = create_operation(user)
        log = OperationLog.objects.create(
            user=user,
            operation=operation,
            action='create'
        )
        
        assert log is not None
        assert log.user == user
        assert log.operation == operation

    def test_operation_log_string_representation(self, create_user, create_operation):
        """Тест строкового представления лога операции."""
        user = create_user()
        operation = create_operation(user, title='Test Operation')
        log = OperationLog.objects.create(
            user=user,
            operation=operation,
            action='create'
        )
        
        expected_str = f"{user.email} - create - Test Operation"
        assert str(log) == expected_str


@pytest.mark.django_db
class TestEdgeCases:
    """Тесты для крайних случаев."""

    def test_operation_without_category(self, api_client, authenticated_user, create_wallet):
        """Тест создания операции без категории."""
        wallet = create_wallet(authenticated_user)
        
        operation_data = {
            'amount': '100.00',
            'title': 'Operation without category',
            'operation_type': 'transfer',  # Переводы могут быть без категории
            'wallet': wallet.id,
            'date': timezone.now().isoformat()
        }
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_operation_without_wallet(self, api_client, authenticated_user, create_category):
        """Тест создания операции без кошелька."""
        category = create_category(authenticated_user)
        
        operation_data = {
            'amount': '100.00',
            'title': 'Operation without wallet',
            'operation_type': 'income',
            'category': category.id,
            'date': timezone.now().isoformat()
        }
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_recurring_operation(self, api_client, authenticated_user, operation_data):
        """Тест создания повторяющейся операции."""
        operation_data['is_recurring'] = True
        operation_data['recurring_pattern'] = {
            'frequency': 'monthly',
            'interval': 1
        }
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_recurring'] is True

    def test_invalid_recurring_pattern(self, api_client, authenticated_user, operation_data):
        """Тест создания операции с невалидным паттерном повторения."""
        operation_data['is_recurring'] = True
        operation_data['recurring_pattern'] = {
            'frequency': 'invalid',
            'interval': 1
        }
        
        url = reverse('operation-list')
        response = api_client.post(url, operation_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST