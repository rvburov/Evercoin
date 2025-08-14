from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User
from wallets.models import Wallet
from categories.models import Category
from core.constants.currencies import CURRENCIES


class Operation(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
        (TRANSFER, 'Transfer'),
    ]
    
    DAILY = 'daily'
    EVERY_3_DAYS = '3days'
    WEEKLY = 'weekly'
    BIWEEKLY = 'biweekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    BIANNUALLY = 'biannually'
    ANNUALLY = 'annually'
    REPEAT_CHOICES = [
        (DAILY, 'Daily'),
        (EVERY_3_DAYS, 'Every 3 days'),
        (WEEKLY, 'Weekly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (BIANNUALLY, 'Biannually'),
        (ANNUALLY, 'Annually'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, related_name='operations')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)
    is_repeat = models.BooleanField(default=False)
    repeat_period = models.CharField(max_length=10, choices=REPEAT_CHOICES, blank=True, null=True)
    repeat_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} {self.wallet.currency if self.wallet else ''}"

    def save(self, *args, **kwargs):
        if self.type == self.TRANSFER:
            self.category = None
        super().save(*args, **kwargs)
