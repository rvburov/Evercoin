# evercoin/backend/api/categories/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.core.constants.icons import CATEGORY_ICONS
from api.core.constants.colors import COLORS
from api.core.constants.default_categories import DEFAULT_CATEGORIES

User = get_user_model()


class Category(models.Model):
    """
    Модель категорий для операций (доходы/расходы)
    """
    
    CATEGORY_TYPES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='categories',
        verbose_name='Пользователь'
    )
    
    name = models.CharField(
        max_length=100, 
        verbose_name='Название категории'
    )
    
    icon = models.CharField(
        max_length=50,
        choices=CATEGORY_ICONS,
        default='shopping',
        verbose_name='Иконка категории'
    )
    
    color = models.CharField(
        max_length=7,
        choices=COLORS,
        default='#4ECDC4',
        verbose_name='Цвет категории'
    )
    
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPES,
        verbose_name='Тип категории'
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Описание категории'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Системная категория'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активная категория'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['category_type', 'name']
        unique_together = ['user', 'name']  # Уникальное название категории для каждого пользователя
        indexes = [
            models.Index(fields=['user', 'category_type']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
    
    def save(self, *args, **kwargs):
        """
        Переопределение сохранения для валидации данных
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Переопределение удаления категории с обработкой связанных операций
        """
        from api.operations.models import Operation
        
        # Проверяем, есть ли связанные операции
        operation_count = self.operations.count()
        
        if operation_count > 0 and not self.is_default:
            # Для пользовательских категорий с операциями создаем исключение
            raise models.ProtectedError(
                "Нельзя удалить категорию с привязанными операциями. "
                "Сначала удалите или перенесите операции.",
                self
            )
        
        # Для системных категорий просто деактивируем
        if self.is_default:
            self.is_active = False
            self.save()
            return
        
        super().delete(*args, **kwargs)
    
    @property
    def operation_count(self):
        """
        Количество операций в этой категории
        """
        return self.operations.count()
    
    @property
    def total_amount(self):
        """
        Общая сумма операций в этой категории
        """
        from django.db.models import Sum
        result = self.operations.aggregate(
            total=Sum('amount')
        )['total'] or 0
        return result
    
    @classmethod
    def create_default_categories(cls, user):
        """
        Создание стандартных категорий для нового пользователя
        """
        categories = []
        for category_data in DEFAULT_CATEGORIES:
            category = cls(
                user=user,
                name=category_data['name'],
                icon=category_data['icon'],
                color=category_data['color'],
                category_type=category_data['category_type'],
                is_default=True,
                is_active=True
            )
            categories.append(category)
        
        cls.objects.bulk_create(categories)
        return categories
    
    def clean(self):
        """
        Валидация данных перед сохранением
        """
        from django.core.exceptions import ValidationError
        
        # Проверка уникальности названия для пользователя
        if self.user and self.name:
            existing_category = Category.objects.filter(
                user=self.user, 
                name=self.name
            )
            if self.pk:  # При обновлении исключаем текущую категорию
                existing_category = existing_category.exclude(pk=self.pk)
            
            if existing_category.exists():
                raise ValidationError({
                    'name': 'У вас уже есть категория с таким названием'
                })
        
        # Проверка, что системные категории нельзя менять пользователю
        if self.pk and self.is_default:
            original = Category.objects.get(pk=self.pk)
            if original.user != self.user:
                raise ValidationError('Нельзя изменять системные категории')


class CategoryMerge(models.Model):
    """
    Модель для отслеживания слияния категорий
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='category_merges',
        verbose_name='Пользователь'
    )
    
    from_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='merged_from',
        verbose_name='Исходная категория'
    )
    
    to_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='merged_to',
        verbose_name='Целевая категория'
    )
    
    operation_count = models.IntegerField(
        default=0,
        verbose_name='Количество перенесенных операций'
    )
    
    merged_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Слияние категорий'
        verbose_name_plural = 'Слияния категорий'
        ordering = ['-merged_at']
    
    def __str__(self):
        return f"Слияние {self.from_category.name} в {self.to_category.name}"