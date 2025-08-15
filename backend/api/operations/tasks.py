# project/backend/api/operations/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import RecurringOperation, Operation
from datetime import timedelta

@shared_task
def process_recurring_operations():
    """Фоновая задача для обработки повторяющихся операций"""
    now = timezone.now()
    recurring_ops = RecurringOperation.objects.filter(
        next_date__lte=now,
        is_active=True
    ).select_related('base_operation')

    for op in recurring_ops:
        # Создаем новую операцию на основе шаблона
        Operation.objects.create(
            user=op.base_operation.user,
            name=op.base_operation.name,
            amount=op.base_operation.amount,
            operation_type=op.base_operation.operation_type,
            category=op.base_operation.category,
            wallet=op.base_operation.wallet,
            date=now,
            description=op.base_operation.description
        )

        # Обновляем следующую дату выполнения
        if op.interval == 'daily':
            op.next_date = now + timedelta(days=1)
        elif op.interval == 'weekly':
            op.next_date = now + timedelta(weeks=1)
        elif op.interval == 'monthly':
            op.next_date = now + timedelta(days=30)  # Упрощенная логика
        elif op.interval == 'yearly':
            op.next_date = now + timedelta(days=365)

        # Проверяем дату окончания
        if op.end_date and op.next_date > op.end_date:
            op.is_active = False

        op.save()
