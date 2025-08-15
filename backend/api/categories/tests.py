# project/backend/api/categories/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category

User = get_user_model()

class CategoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовые категории
        self.food_category = Category.objects.create(
            user=self.user,
            name='Продукты',
            type=Category.EXPENSE,
            icon='food',
            color='#FF5733'
        )
        self.salary_category = Category.objects.create(
            user=self.user,
            name='Зарплата',
            type=Category.INCOME,
            icon='money',
            color='#33FF57',
            is_system=True
        )

    def test_create_category(self):
        """Тест создания новой категории"""
        payload = {
            'name': 'Транспорт',
            'type': Category.EXPENSE,
            'icon': 'car',
            'color': '#3357FF'
        }
        response = self.client.post('/api/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        category = Category.objects.get(id=response.data['id'])
        self.assertEqual(category.name, payload['name'])
        self.assertEqual(category.user, self.user)

    def test_create_child_category(self):
        """Тест создания дочерней категории"""
        payload = {
            'name': 'Рестораны',
            'type': Category.EXPENSE,
            'parent': self.food_category.id,
            'icon': 'restaurant',
            'color': '#FF33A8'
        }
        response = self.client.post('/api/categories/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        category = Category.objects.get(id=response.data['id'])
        self.assertEqual(category.parent, self.food_category)

    def test_delete_system_category(self):
        """Тест попытки удаления системной категории"""
        response = self.client.delete(f'/api/categories/{self.salary_category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Нельзя удалить системную категорию', str(response.data))

    def test_category_tree(self):
        """Тест получения древовидной структуры категорий"""
        # Создаем дочернюю категорию
        Category.objects.create(
            user=self.user,
            name='Фастфуд',
            type=Category.EXPENSE,
            parent=self.food_category
        )
        
        response = self.client.get('/api/categories/tree/?type=expense')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Одна родительская категория
        self.assertEqual(len(response.data[0]['children']), 1)  # С одной дочерней
