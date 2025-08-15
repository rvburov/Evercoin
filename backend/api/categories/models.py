# project/backend/api/categories/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from api.core.constants import icons, colors

class Category(models.Model):
    """
    Модель категории для операций (доходов/расходов).
    Содержит информацию о типе, названии и визуальном оформлении категории.
    """
    
    # Типы категорий
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = (
        (INCOME, _('Доход')),
        (EXPENSE, _('Расход')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('Пользователь')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Например: Продукты, Транспорт, Зарплата')
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name=_('Тип категории')
    )
    icon = models.CharField(
        max_length=50,
        default='category',
        verbose_name=_('Иконка'),
        help_text=_('Код иконки из доступного набора')
    )
    color = models.CharField(
        max_length=7,
        default=colors.DEFAULT_CATEGORY_COLOR,
        verbose_name=_('Цвет'),
        help_text=_('HEX-код цвета, например #FF5733')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительская категория')
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_('Системная категория'),
        help_text=_('Системные категории нельзя удалять или изменять')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name', 'type'],
                name='unique_category_name_per_user_and_type'
            )
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

    def save(self, *args, **kwargs):
        """При сохранении проверяем, что родительская категория того же типа"""
        if self.parent and self.parent.type != self.type:
            raise ValueError(
                "Родительская категория должна быть того же типа"
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Запрещаем удаление системных категорий"""
        if self.is_system:
            raise models.ProtectedError(
                "Нельзя удалить системную категорию",
                self
            )
        super().delete(*args, **kwargs)
