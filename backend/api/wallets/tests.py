# project/backend/api/notifications/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Wallet

User = get_user_model()

class WalletTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовые счета
        self.wallet1 = Wallet.objects.create(
            user=self.user,
            name='Основной счет',
            balance=1000,
            currency='RUB',
            is_default=True
        )
        self.wallet2 = Wallet.objects.create(
            user=self.user,
            name='Дополнительный счет',
            balance=500,
            currency='USD'
        )

    def test_create_wallet(self):
        """Тест создания нового счета"""
        payload = {
            'name': 'Кредитная карта',
            'balance': 0,
            'currency': 'EUR',
            'icon': 'credit-card',
            'color': '#FF0000'
        }
        response = self.client.post('/api/wallets/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        wallet = Wallet.objects.get(id=response.data['id'])
        self.assertEqual(wallet.name, payload['name'])
        self.assertEqual(wallet.user, self.user)

    def test_default_wallet_auto_update(self):
        """Тест автоматического обновления счета по умолчанию"""
        # Создаем новый счет и делаем его по умолчанию
        payload = {
            'name': 'Новый основной счет',
            'balance': 0,
            'currency': 'RUB',
            'is_default': True
        }
        response = self.client.post('/api/wallets/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что предыдущий счет по умолчанию больше не является таковым
        self.wallet1.refresh_from_db()
        self.assertFalse(self.wallet1.is_default)

    def test_transfer_funds(self):
        """Тест перевода средств между счетами"""
        payload = {
            'from_wallet': self.wallet1.id,
            'to_wallet': self.wallet2.id,
            'amount': 300,
            'description': 'Тестовый перевод'
        }
        response = self.client.post('/api/wallets/transfer/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем обновленные балансы
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, 700)  # 1000 - 300
        self.assertEqual(self.wallet2.balance, 800)  # 500 + 300

    def test_insufficient_funds_transfer(self):
        """Тест попытки перевода при недостаточных средствах"""
        payload = {
            'from_wallet': self.wallet1.id,
            'to_wallet': self.wallet2.id,
            'amount': 1500  # Больше чем баланс wallet1 (1000)
        }
        response = self.client.post('/api/wallets/transfer/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
