# project/backend/api/notifications/tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import Notification
from operations.models import RecurringOperation
from datetime import timedelta

@shared_task
def create_recurring_operation_notifications():
    """
    Фоновая задача для создания уведомлений о предстоящих повторяющихся операциях.
    Запускается ежедневно.
    """
    now = timezone.now()
    start_date = now + timedelta(days=1)  # Уведомления на следующий день
    end_date = now + timedelta(days=3)    # На 3 дня вперед

    recurring_ops = RecurringOperation.objects.filter(
        next_date__range=(start_date, end_date),
        is_active=True
    ).select_related('base_operation')

    for op in recurring_ops:
        try:
            Notification.objects.create(
                user=op.base_operation.user,
                operation=op.base_operation,
                notification_type='upcoming',
                title=f"Скоро: {op.base_operation.name}",
                message=f"Сумма: {op.base_operation.amount} {op.base_operation.wallet.currency}",
                notification_date=op.next_date - timedelta(days=1)  # За день до операции
            )
        except Exception as e:
            # Логирование ошибки
            print(f"Error creating notification for operation {op.id}: {str(e)}")

@shared_task
def cleanup_old_notifications():
    """
    Задача для очистки старых уведомлений.
    Удаляет прочитанные уведомления старше 30 дней.
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lte=cutoff_date
    ).delete()
    
    return f"Удалено {deleted_count} старых уведомлений"
