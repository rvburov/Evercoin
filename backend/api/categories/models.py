# project/backend/api/categories/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()

class Category(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    
    OPERATION_TYPES = [
        (INCOME, 'Доход'),
        (EXPENSE, 'Расход'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='categories',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100, 
        validators=[MinLengthValidator(2)],
        verbose_name='Название категории'
    )
    operation_type = models.CharField(
        max_length=10, 
        choices=OPERATION_TYPES,
        verbose_name='Тип операции'
    )
    icon = models.CharField(
        max_length=50,
        verbose_name='Иконка'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        help_text='HEX код цвета (например, #FF5733)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['operation_type', 'name']
        unique_together = ['user', 'name', 'operation_type']
        indexes = [
            models.Index(fields=['user', 'operation_type']),
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_operation_type_display()})"
    
    def delete(self, *args, **kwargs):
        # При удалении категории удаляем все связанные операции
        from operations.models import Operation
        Operation.objects.filter(category=self).delete()
        super().delete(*args, **kwargs)
