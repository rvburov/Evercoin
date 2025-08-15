# project/backend/api/notifications/urls.py
from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkAsReadView,
    create_upcoming_notification
)

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', NotificationMarkAsReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/create/', create_upcoming_notification, name='notification-create'),
]
