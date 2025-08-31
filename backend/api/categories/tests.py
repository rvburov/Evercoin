# evercoin/backend/api/categories/tests.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.categories.models import Category, CategoryBudget

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
def create_category(create_user):
    """Фикстура для создания категории."""
    def _create_category(user=None, name='Test Category', category_type='expense', **kwargs):
        if user is None:
            user = create_user()
        return Category.objects.create(
            user=user,
            name=name,
            type=category_type,
            **kwargs
        )
    return _create_category


@pytest.fixture
def create_category_budget(create_user, create_category):
    """Фикстура для создания бюджета категории."""
    def _create_category_budget(user=None, category=None, amount=1000.00, **kwargs):
        if user is None:
            user = create_user()
        if category is None:
            category = create_category(user=user)
        return CategoryBudget.objects.create(
            user=user,
            category=category,
            amount=amount,
            **kwargs
        )
    return _create_category_budget


@pytest.mark.django_db
class TestCategoryViewSet:
    """Тесты для представления категорий."""

    def test_list_categories_unauthenticated(self, api_client):
        """Тест получения списка категорий без аутентификации."""
        url = reverse('category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_categories_authenticated(self, api_client, authenticated_user, create_category):
        """Тест получения списка категорий с аутентификацией."""
        create_category(user=authenticated_user, name='Category 1')
        create_category(user=authenticated_user, name='Category 2')
        
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_only_user_categories(self, api_client, create_user, create_category):
        """Тест, что пользователь видит только свои категории."""
        user1 = create_user(email='user1@example.com')
        user2 = create_user(email='user2@example.com')
        
        create_category(user=user1, name='User1 Category')
        create_category(user=user2, name='User2 Category')
        
        # Аутентифицируем user1
        refresh = RefreshToken.for_user(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'User1 Category'

    def test_create_category(self, api_client, authenticated_user):
        """Тест создания категории."""
        url = reverse('category-list')
        category_data = {
            'name': 'New Category',
            'type': 'expense',
            'icon': 'shopping',
            'color': '#3B82F6'
        }
        response = api_client.post(url, category_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='New Category').exists()

    def test_create_category_duplicate_name_same_type(self, api_client, authenticated_user, create_category):
        """Тест создания категории с дублирующимся именем и типом."""
        create_category(user=authenticated_user, name='Test Category', category_type='expense')
        
        url = reverse('category-list')
        category_data = {
            'name': 'Test Category',
            'type': 'expense',
            'icon': 'food',
            'color': '#EF4444'
        }
        response = api_client.post(url, category_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_duplicate_name_different_type(self, api_client, authenticated_user, create_category):
        """Тест создания категории с дублирующимся именем, но разным типом."""
        create_category(user=authenticated_user, name='Test Category', category_type='expense')
        
        url = reverse('category-list')
        category_data = {
            'name': 'Test Category',
            'type': 'income',
            'icon': 'salary',
            'color': '#10B981'
        }
        response = api_client.post(url, category_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_category(self, api_client, authenticated_user, create_category):
        """Тест получения детальной информации о категории."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-detail', kwargs={'pk': category.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Category'

    def test_update_category(self, api_client, authenticated_user, create_category):
        """Тест обновления категории."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-detail', kwargs={'pk': category.pk})
        update_data = {'name': 'Updated Category'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == 'Updated Category'

    def test_delete_category(self, api_client, authenticated_user, create_category):
        """Тест удаления категории."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-detail', kwargs={'pk': category.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=category.pk).exists()

    def test_category_tree(self, api_client, authenticated_user, create_category):
        """Тест получения дерева категорий."""
        parent_category = create_category(user=authenticated_user, name='Parent')
        create_category(user=authenticated_user, name='Child', parent=parent_category)
        
        url = reverse('category-tree')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert len(response.data[0]['subcategories']) == 1

    def test_categories_by_type(self, api_client, authenticated_user, create_category):
        """Тест получения категорий по типу."""
        create_category(user=authenticated_user, name='Expense Category', category_type='expense')
        create_category(user=authenticated_user, name='Income Category', category_type='income')
        
        url = reverse('category-by-type')
        response = api_client.get(url, {'type': 'expense'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Expense Category'

    def test_categories_by_type_invalid(self, api_client, authenticated_user):
        """Тест получения категорий по неверному типу."""
        url = reverse('category-by-type')
        response = api_client.get(url, {'type': 'invalid'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_category_analytics(self, api_client, authenticated_user, create_category):
        """Тест аналитики категорий."""
        create_category(user=authenticated_user)
        
        url = reverse('category-analytics')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'categories' in response.data
        assert 'total_operations' in response.data
        assert 'total_amount' in response.data

    def test_category_operations(self, api_client, authenticated_user, create_category):
        """Тест получения операций категории."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-operations', kwargs={'pk': category.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data


@pytest.mark.django_db
class TestCategoryBudgetViewSet:
    """Тесты для представления бюджетов категорий."""

    def test_list_budgets_unauthenticated(self, api_client):
        """Тест получения списка бюджетов без аутентификации."""
        url = reverse('category-budget-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_budgets_authenticated(self, api_client, authenticated_user, create_category_budget):
        """Тест получения списка бюджетов с аутентификацией."""
        create_category_budget(user=authenticated_user)
        
        url = reverse('category-budget-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_budget(self, api_client, authenticated_user, create_category):
        """Тест создания бюджета."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-budget-list')
        budget_data = {
            'category': category.pk,
            'amount': '1500.00',
            'period': 'monthly'
        }
        response = api_client.post(url, budget_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert CategoryBudget.objects.filter(amount=1500.00).exists()

    def test_create_budget_other_user_category(self, api_client, create_user, create_category):
        """Тест создания бюджета с категорией другого пользователя."""
        user1 = create_user(email='user1@example.com')
        user2 = create_user(email='user2@example.com')
        category = create_category(user=user1)
        
        # Аутентифицируем user2
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('category-budget-list')
        budget_data = {
            'category': category.pk,
            'amount': '1500.00',
            'period': 'monthly'
        }
        response = api_client.post(url, budget_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_budget(self, api_client, authenticated_user, create_category_budget):
        """Тест получения детальной информации о бюджете."""
        budget = create_category_budget(user=authenticated_user)
        
        url = reverse('category-budget-detail', kwargs={'pk': budget.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['amount'] == '1000.00'

    def test_update_budget(self, api_client, authenticated_user, create_category_budget):
        """Тест обновления бюджета."""
        budget = create_category_budget(user=authenticated_user)
        
        url = reverse('category-budget-detail', kwargs={'pk': budget.pk})
        update_data = {'amount': '2000.00'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        budget.refresh_from_db()
        assert budget.amount == 2000.00

    def test_delete_budget(self, api_client, authenticated_user, create_category_budget):
        """Тест удаления бюджета."""
        budget = create_category_budget(user=authenticated_user)
        
        url = reverse('category-budget-detail', kwargs={'pk': budget.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CategoryBudget.objects.filter(pk=budget.pk).exists()

    def test_active_budgets(self, api_client, authenticated_user, create_category_budget):
        """Тест получения активных бюджетов."""
        create_category_budget(user=authenticated_user, is_active=True)
        create_category_budget(user=authenticated_user, is_active=False)
        
        url = reverse('category-budget-active')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_budgets_overview(self, api_client, authenticated_user, create_category_budget):
        """Тест получения обзора бюджетов."""
        create_category_budget(user=authenticated_user)
        
        url = reverse('category-budget-overview')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'spent_amount' in response.data[0]
        assert 'remaining_amount' in response.data[0]
        assert 'progress_percentage' in response.data[0]


@pytest.mark.django_db
class TestCategoryConstantsViewSet:
    """Тесты для представления констант категорий."""

    def test_get_icons_unauthenticated(self, api_client):
        """Тест получения иконок без аутентификации."""
        url = reverse('category-constants-icons')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_icons_authenticated(self, api_client, authenticated_user):
        """Тест получения иконок с аутентификацией."""
        url = reverse('category-constants-icons')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0

    def test_get_colors_authenticated(self, api_client, authenticated_user):
        """Тест получения цветов с аутентификацией."""
        url = reverse('category-constants-colors')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) > 0

    def test_get_types_authenticated(self, api_client, authenticated_user):
        """Тест получения типов категорий с аутентификацией."""
        url = reverse('category-constants-types')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2


@pytest.mark.django_db
class TestCategoryModel:
    """Тесты для модели Category."""

    def test_category_creation(self, create_user):
        """Тест создания категории."""
        user = create_user()
        category = Category.objects.create(
            user=user,
            name='Test Category',
            type='expense',
            icon='shopping',
            color='#3B82F6'
        )
        
        assert category.name == 'Test Category'
        assert category.type == 'expense'
        assert category.user == user

    def test_category_string_representation(self, create_category):
        """Тест строкового представления категории."""
        category = create_category()
        assert str(category) == f"{category.user.email} - Test Category (Расход)"

    def test_category_has_children_property(self, create_category):
        """Тест свойства has_children."""
        parent_category = create_category(name='Parent')
        child_category = create_category(name='Child', parent=parent_category)
        
        assert parent_category.has_children is True
        assert child_category.has_children is False

    def test_category_full_name_property(self, create_category):
        """Тест свойства full_name."""
        parent_category = create_category(name='Parent')
        child_category = create_category(name='Child', parent=parent_category)
        
        assert parent_category.full_name == 'Parent'
        assert child_category.full_name == 'Parent → Child'

    def test_category_delete_with_operations(self, create_category):
        """Тест удаления категории с операциями."""
        from api.operations.models import Operation
        from api.wallets.models import Wallet
        
        category = create_category()
        user = category.user
        
        # Создаем кошелек и операцию
        wallet = Wallet.objects.create(
            user=user,
            name='Test Wallet',
            balance=1000.00,
            currency='RUB'
        )
        operation = Operation.objects.create(
            user=user,
            wallet=wallet,
            category=category,
            amount=100.00,
            operation_type='expense',
            description='Test operation'
        )
        
        # Удаляем категорию
        category.delete()
        
        # Проверяем, что операция перемещена в категорию "Без категории"
        operation.refresh_from_db()
        assert operation.category.name == 'Без категории'
        assert operation.category.is_default is True


@pytest.mark.django_db
class TestCategoryBudgetModel:
    """Тесты для модели CategoryBudget."""

    def test_budget_creation(self, create_category_budget):
        """Тест создания бюджета."""
        budget = create_category_budget()
        
        assert budget.amount == 1000.00
        assert budget.period == 'monthly'
        assert budget.is_active is True

    def test_budget_string_representation(self, create_category_budget):
        """Тест строкового представления бюджета."""
        budget = create_category_budget()
        expected_str = f"{budget.category.name} - 1000.00 (Ежемесячно)"
        assert str(budget) == expected_str

    def test_budget_spent_amount_property(self, create_category_budget):
        """Тест свойства spent_amount."""
        budget = create_category_budget()
        assert budget.spent_amount == 0.00

    def test_budget_remaining_amount_property(self, create_category_budget):
        """Тест свойства remaining_amount."""
        budget = create_category_budget()
        assert budget.remaining_amount == 1000.00

    def test_budget_progress_percentage_property(self, create_category_budget):
        """Тест свойства progress_percentage."""
        budget = create_category_budget()
        assert budget.progress_percentage == 0.00

    def test_budget_is_valid_method(self, create_category_budget):
        """Тест метода is_valid."""
        budget = create_category_budget()
        assert budget.is_active is True


@pytest.mark.django_db
class TestIntegration:
    """Интеграционные тесты для категорий."""

    def test_complete_category_workflow(self, api_client, authenticated_user):
        """Тест полного рабочего процесса категорий."""
        # 1. Создание категории
        create_url = reverse('category-list')
        category_data = {
            'name': 'Integration Category',
            'type': 'expense',
            'icon': 'shopping',
            'color': '#3B82F6'
        }
        create_response = api_client.post(create_url, category_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        
        category_id = create_response.data['id']
        
        # 2. Получение категории
        detail_url = reverse('category-detail', kwargs={'pk': category_id})
        detail_response = api_client.get(detail_url)
        assert detail_response.status_code == status.HTTP_200_OK
        
        # 3. Обновление категории
        update_data = {'name': 'Updated Integration Category'}
        update_response = api_client.patch(detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        
        # 4. Создание бюджета для категории
        budget_url = reverse('category-budget-list')
        budget_data = {
            'category': category_id,
            'amount': '2000.00',
            'period': 'monthly'
        }
        budget_response = api_client.post(budget_url, budget_data, format='json')
        assert budget_response.status_code == status.HTTP_201_CREATED
        
        budget_id = budget_response.data['id']
        
        # 5. Получение обзора бюджетов
        overview_url = reverse('category-budget-overview')
        overview_response = api_client.get(overview_url)
        assert overview_response.status_code == status.HTTP_200_OK
        assert len(overview_response.data) == 1
        
        # 6. Удаление бюджета
        budget_detail_url = reverse('category-budget-detail', kwargs={'pk': budget_id})
        delete_budget_response = api_client.delete(budget_detail_url)
        assert delete_budget_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. Удаление категории
        delete_category_response = api_client.delete(detail_url)
        assert delete_category_response.status_code == status.HTTP_204_NO_CONTENT

    def test_category_tree_workflow(self, api_client, authenticated_user, create_category):
        """Тест рабочего процесса дерева категорий."""
        # Создаем иерархию категорий
        parent = create_category(user=authenticated_user, name='Parent')
        child1 = create_category(user=authenticated_user, name='Child 1', parent=parent)
        child2 = create_category(user=authenticated_user, name='Child 2', parent=parent)
        
        # Получаем дерево категорий
        tree_url = reverse('category-tree')
        tree_response = api_client.get(tree_url)
        
        assert tree_response.status_code == status.HTTP_200_OK
        assert len(tree_response.data) == 1  # Только корневые категории
        assert len(tree_response.data[0]['subcategories']) == 2  # Две дочерние категории


@pytest.mark.django_db
class TestValidation:
    """Тесты валидации категорий."""

    def test_category_name_length_validation(self, api_client, authenticated_user):
        """Тест валидации длины названия категории."""
        url = reverse('category-list')
        long_name = 'A' * 256  # Превышает лимит в 255 символов
        category_data = {
            'name': long_name,
            'type': 'expense',
            'icon': 'shopping',
            'color': '#3B82F6'
        }
        response = api_client.post(url, category_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_budget_amount_validation(self, api_client, authenticated_user, create_category):
        """Тест валидации суммы бюджета."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-budget-list')
        budget_data = {
            'category': category.pk,
            'amount': '-100.00',  # Отрицательная сумма
            'period': 'monthly'
        }
        response = api_client.post(url, budget_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_budget_period_validation(self, api_client, authenticated_user, create_category):
        """Тест валидации периода бюджета."""
        category = create_category(user=authenticated_user)
        
        url = reverse('category-budget-list')
        budget_data = {
            'category': category.pk,
            'amount': '1000.00',
            'period': 'invalid_period'  # Неверный период
        }
        response = api_client.post(url, budget_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST