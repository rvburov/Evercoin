# project/backend/api/operations/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from wallets.models import Wallet
from categories.models import Category
from .models import Operation

User = get_user_model()

class OperationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass'
        )
        self.wallet = Wallet.objects.create(
            user=self.user,
            name='Test Wallet',
            balance=1000
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            type='expense'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_operation(self):
        """Тест создания новой операции"""
        payload = {
            'name': 'Test Operation',
            'amount': '100.00',
            'operation_type': 'expense',
            'wallet': self.wallet.id,
            'category': self.category.id,
            'date': '2023-01-01T00:00:00Z'
        }
        res = self.client.post('/api/operations/', payload)
        self.assertEqual(res.status_code, 201)
        operation = Operation.objects.get(id=res.data['id'])
        self.assertEqual(operation.name, payload['name'])
        self.assertEqual(float(operation.amount), float(payload['amount']))

    def test_insufficient_balance(self):
        """Тест проверки недостаточного баланса"""
        payload = {
            'name': 'Expensive Operation',
            'amount': '1500.00',  # Больше чем баланс кошелька
            'operation_type': 'expense',
            'wallet': self.wallet.id,
            'date': '2023-01-01T00:00:00Z'
        }
        res = self.client.post('/api/operations/', payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Недостаточно средств', res.data['non_field_errors'][0])
