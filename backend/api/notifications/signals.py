# project/backend/api/notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from operations.models import Operation
from .models import Notification
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=Operation)
def create_operation_notification(sender, instance, created, **kwargs):
    """
    Сигнал для создания уведомления при создании операции с настройками уведомлений.
    """
    if created and hasattr(instance, 'notification_settings'):
        settings = instance.notification_settings
        Notification.objects.create(
            user=instance.user,
            operation=instance,
            notification_type='reminder',
            title=f"Напоминание: {instance.name}",
            message=f"Сумма: {instance.amount} {instance.wallet.currency}",
            notification_date=timezone.now() + timedelta(days=settings.days_before)
        )
