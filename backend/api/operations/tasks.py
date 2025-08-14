from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Operation


@shared_task
def create_repeated_operations():
    today = timezone.now().date()
    repeat_operations = Operation.objects.filter(
        is_repeat=True,
        repeat_end_date__gte=today
    )
    
    for operation in repeat_operations:
        last_operation = Operation.objects.filter(
            user=operation.user,
            title=operation.title,
            amount=operation.amount,
            type=operation.type,
            wallet=operation.wallet,
            category=operation.category,
            is_repeat=False,
            date__date__gte=today - timedelta(days=1)
        ).first()
        
        if not last_operation:
            next_date = today
        else:
            if operation.repeat_period == 'daily':
                next_date = last_operation.date.date() + timedelta(days=1)
            elif operation.repeat_period == '3days':
                next_date = last_operation.date.date() + timedelta(days=3)
            elif operation.repeat_period == 'weekly':
                next_date = last_operation.date.date() + timedelta(weeks=1)
            elif operation.repeat_period == 'biweekly':
                next_date = last_operation.date.date() + timedelta(weeks=2)
            elif operation.repeat_period == 'monthly':
                next_date = last_operation.date.date() + timedelta(days=30)
            elif operation.repeat_period == 'quarterly':
                next_date = last_operation.date.date() + timedelta(days=90)
            elif operation.repeat_period == 'biannually':
                next_date = last_operation.date.date() + timedelta(days=180)
            elif operation.repeat_period == 'annually':
                next_date = last_operation.date.date() + timedelta(days=365)
            else:
                continue
        
        if next_date <= today:
            Operation.objects.create(
                user=operation.user,
                title=operation.title,
                amount=operation.amount,
                type=operation.type,
                wallet=operation.wallet,
                category=operation.category,
                comment=operation.comment,
                is_repeat=False,
                date=next_date
            )
