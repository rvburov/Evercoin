# project/backend/api/operations/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from .models import Operation
from wallets.models import Wallet
from categories.models import Category

User = get_user_model()

class OperationTests(APITestCase):
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
            balance=Decimal('1000.00'),
            currency='RUB'
        )
        
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            operation_type='expense',
            icon='food',
            color='#FF0000'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_income_operation(self):
        """Тест создания операции дохода"""
        data = {
            'amount': '100.00',
            'title': 'Test Income',
            'description': 'Test description',
            'operation_type': 'income',
            'date': timezone.now(),
            'wallet': self.wallet.id,
            'category': self.category.id
        }
        
        response = self.client.post('/api/operations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Operation.objects.count(), 1)
        
        # Проверка обновления баланса
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1100.00'))
    
    def test_create_expense_operation(self):
        """Тест создания операции расхода"""
        data = {
            'amount': '100.00',
            'title': 'Test Expense',
            'description': 'Test description',
            'operation_type': 'expense',
            'date': timezone.now(),
            'wallet': self.wallet.id,
            'category': self.category.id
        }
        
        response = self.client.post('/api/operations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверка обновления баланса
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('900.00'))
    
    def test_create_expense_with_insufficient_funds(self):
        """Тест создания расхода при недостаточных средствах"""
        data = {
            'amount': '2000.00',
            'title': 'Large Expense',
            'operation_type': 'expense',
            'date': timezone.now(),
            'wallet': self.wallet.id,
            'category': self.category.id
        }
        
        response = self.client.post('/api/operations/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Недостаточно средств на счете', str(response.data))
    
    def test_list_operations(self):
        """Тест получения списка операций"""
        # Создаем тестовые операции
        Operation.objects.create(
            user=self.user,
            wallet=self.wallet,
            category=self.category,
            amount=Decimal('100.00'),
            title='Test Operation 1',
            operation_type='income',
            date=timezone.now()
        )
        
        Operation.objects.create(
            user=self.user,
            wallet=self.wallet,
            category=self.category,
            amount=Decimal('50.00'),
            title='Test Operation 2',
            operation_type='expense',
            date=timezone.now() - timedelta(days=1)
        )
        
        response = self.client.get('/api/operations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_income_summary(self):
        """Тест сводки по доходам"""
        # Создаем операции дохода
        for i in range(3):
            Operation.objects.create(
                user=self.user,
                wallet=self.wallet,
                category=self.category,
                amount=Decimal(f'{100 + i * 50}.00'),
                title=f'Income {i}',
                operation_type='income',
                date=timezone.now()
            )
        
        response = self.client.get('/api/operations/income_summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], Decimal('300.00'))
    
    def test_analytics(self):
        """Тест аналитики операций"""
        # Создаем операции за текущий месяц
        for i in range(5):
            Operation.objects.create(
                user=self.user,
                wallet=self.wallet,
                category=self.category,
                amount=Decimal('100.00'),
                title=f'Operation {i}',
                operation_type='income' if i % 2 == 0 else 'expense',
                date=timezone.now() - timedelta(days=i)
            )
        
        response = self.client.get('/api/operations/analytics/?period=month')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
