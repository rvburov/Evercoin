# project/backend/api/categories/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone

from .models import Category
from operations.models import Operation
from wallets.models import Wallet

User = get_user_model()

class CategoryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.wallet = Wallet.objects.create(
            user=self.user,
            name='Test Wallet',
            balance=1000.00,
            currency='RUB'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_category(self):
        """Тест создания категории"""
        data = {
            'name': 'Test Category',
            'operation_type': 'expense',
            'icon': 'food',
            'color': '#FF6B6B'
        }
        
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        
        category = Category.objects.first()
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.operation_type, 'expense')
        self.assertEqual(category.user, self.user)
    
    def test_create_duplicate_category(self):
        """Тест создания дубликата категории"""
        Category.objects.create(
            user=self.user,
            name='Test Category',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        data = {
            'name': 'Test Category',
            'operation_type': 'expense',
            'icon': 'transport',
            'color': '#4ECDC4'
        }
        
        response = self.client.post('/api/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('уже существует', str(response.data))
    
    def test_list_categories(self):
        """Тест получения списка категорий"""
        # Создаем тестовые категории
        Category.objects.create(
            user=self.user,
            name='Food',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        Category.objects.create(
            user=self.user,
            name='Salary',
            operation_type='income',
            icon='salary',
            color='#00B894'
        )
        
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_categories_by_type(self):
        """Тест фильтрации категорий по типу"""
        Category.objects.create(
            user=self.user,
            name='Food',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        Category.objects.create(
            user=self.user,
            name='Salary',
            operation_type='income',
            icon='salary',
            color='#00B894'
        )
        
        # Фильтрация по расходам
        response = self.client.get('/api/categories/?type=expense')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['operation_type'], 'expense')
        
        # Фильтрация по доходам
        response = self.client.get('/api/categories/?type=income')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['operation_type'], 'income')
    
    def test_update_category(self):
        """Тест обновления категории"""
        category = Category.objects.create(
            user=self.user,
            name='Food',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        data = {
            'name': 'Updated Food',
            'operation_type': 'expense',
            'icon': 'groceries',
            'color': '#D63031'
        }
        
        response = self.client.put(f'/api/categories/{category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Food')
        self.assertEqual(category.icon, 'groceries')
        self.assertEqual(category.color, '#D63031')
    
    def test_delete_category(self):
        """Тест удаления категории с удалением связанных операций"""
        category = Category.objects.create(
            user=self.user,
            name='Food',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        # Создаем операцию связанную с категорией
        operation = Operation.objects.create(
            user=self.user,
            wallet=self.wallet,
            category=category,
            amount=100.00,
            title='Test Operation',
            operation_type='expense',
            date=timezone.now()
        )
        
        # Удаляем категорию
        response = self.client.delete(f'/api/categories/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Проверяем что категория удалена
        self.assertEqual(Category.objects.count(), 0)
        
        # Проверяем что связанная операция также удалена
        self.assertEqual(Operation.objects.count(), 0)
    
    def test_available_icons(self):
        """Тест получения доступных иконок"""
        response = self.client.get('/api/categories/available_icons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
    
    def test_available_colors(self):
        """Тест получения доступных цветов"""
        response = self.client.get('/api/categories/available_colors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
    
    def test_categories_with_stats(self):
        """Тест получения категорий со статистикой"""
        category = Category.objects.create(
            user=self.user,
            name='Food',
            operation_type='expense',
            icon='food',
            color='#FF6B6B'
        )
        
        # Создаем операцию для статистики
        Operation.objects.create(
            user=self.user,
            wallet=self.wallet,
            category=category,
            amount=150.00,
            title='Lunch',
            operation_type='expense',
            date=timezone.now()
        )
        
        response = self.client.get('/api/categories/with_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('categories', response.data)
        self.assertIn('total_stats', response.data)
        
        category_data = response.data['categories'][0]
        self.assertEqual(category_data['operation_count'], 1)
        self.assertEqual(category_data['total_amount'], '150.00')
