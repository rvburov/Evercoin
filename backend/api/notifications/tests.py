# project/backend/api/notifications/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from operations.models import Operation
from .models import Notification

User = get_user_model()

class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем тестовую операцию
        self.operation = Operation.objects.create(
            user=self.user,
            name='Тестовая операция',
            amount=100,
            operation_type='expense'
        )
        
        # Создаем тестовые уведомления
        self.notification1 = Notification.objects.create(
            user=self.user,
            operation=self.operation,
            title='Тестовое уведомление 1',
            notification_date=timezone.now() - timedelta(days=1),
            is_read=False
        )
        self.notification2 = Notification.objects.create(
            user=self.user,
            operation=self.operation,
            title='Тестовое уведомление 2',
            notification_date=timezone.now() + timedelta(days=1),
            is_read=True
        )

    def test_get_unread_notifications(self):
        """Тест получения списка непрочитанных уведомлений"""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Только одно непрочитанное
        self.assertEqual(response.data[0]['id'], self.notification1.id)

    def test_mark_notification_as_read(self):
        """Тест пометки уведомления как прочитанного"""
        response = self.client.patch(
            f'/api/notifications/{self.notification1.id}/',
            {'is_read': True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_all_notifications_as_read(self):
        """Тест пометки всех уведомлений как прочитанных"""
        response = self.client.patch(
            '/api/notifications/mark-all-read/',
            {'all': True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_create_notification(self):
        """Тест создания уведомления"""
        payload = {
            'operation': self.operation.id,
            'notification_type': 'upcoming',
            'title': 'Новое уведомление',
            'message': 'Тестовое сообщение',
            'notification_date': timezone.now() + timedelta(days=1)
        }
        response = self.client.post('/api/notifications/create/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 3)
