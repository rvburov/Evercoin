# evercoin/backend/api/categories/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.core.constants.icons import CATEGORY_ICONS
from api.core.constants.colors import COLORS

User = get_user_model()

class Category(models.Model):
    CATEGORY_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, choices=CATEGORY_ICONS, default='shopping')
    color = models.CharField(max_length=7, choices=COLORS, default='#3B82F6')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    budget_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['type', 'name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name', 'type'], name='unique_category_name_per_user_type')
        ]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        # Ограничение длины названия
        if len(self.name) > 255:
            self.name = self.name[:255]
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        from api.operations.models import Operation
        
        # Получаем категорию "Без категории" или создаем ее
        uncategorized_category, created = Category.objects.get_or_create(
            user=self.user,
            name="Без категории",
            type=self.type,
            defaults={
                'icon': 'question',
                'color': '#78716C',
                'is_default': True
            }
        )
        
        # Переносим операции в категорию "Без категории"
        Operation.objects.filter(category=self).update(category=uncategorized_category)
        
        # Переносим подкатегории на уровень выше
        if self.subcategories.exists():
            for subcategory in self.subcategories.all():
                subcategory.parent = self.parent
                subcategory.save()
        
        super().delete(*args, **kwargs)
    
    @property
    def has_children(self):
        return self.subcategories.exists()
    
    @property
    def full_name(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

class CategoryBudget(models.Model):
    PERIOD_CHOICES = (
        ('monthly', 'Ежемесячно'),
        ('weekly', 'Еженедельно'),
        ('yearly', 'Ежегодно'),
        ('custom', 'Произвольный'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Бюджет категории'
        verbose_name_plural = 'Бюджеты категорий'
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.get_period_display()})"
    
    @property
    def spent_amount(self):
        from api.operations.models import Operation
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum
        
        now = timezone.now()
        
        if self.period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
        elif self.period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif self.period == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            start_date = self.start_date
            end_date = self.end_date or now
        
        spent = Operation.objects.filter(
            category=self.category,
            operation_type='expense',
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return spent
    
    @property
    def remaining_amount(self):
        return self.amount - self.spent_amount
    
    @property
    def progress_percentage(self):
        if self.amount == 0:
            return 0
        return min(100, (self.spent_amount / self.amount) * 100)
