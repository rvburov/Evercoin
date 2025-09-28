# evercoin/backend/api/categories/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_category_name_unique_per_user(value, user):
    """
    Валидация уникальности названия категории для пользователя
    """
    from .models import Category
    
    if Category.objects.filter(user=user, name=value).exists():
        raise ValidationError(_('У вас уже есть категория с таким названием'))


def validate_category_type(value):
    """
    Валидация типа категории
    """
    valid_types = ['income', 'expense']
    if value not in valid_types:
        raise ValidationError(_('Недопустимый тип категории'))


def validate_category_icon(value):
    """
    Валидация иконки категории
    """
    from api.core.constants.icons import CATEGORY_ICONS
    
    valid_icons = [icon[0] for icon in CATEGORY_ICONS]
    if value not in valid_icons:
        raise ValidationError(_('Недопустимая иконка категории'))


def validate_category_color(value):
    """
    Валидация цвета категории
    """
    from api.core.constants.colors import COLORS
    
    valid_colors = [color[0] for color in COLORS]
    if value not in valid_colors:
        raise ValidationError(_('Недопустимый цвет категории'))


def validate_not_default_category(category):
    """
    Валидация, что категория не является системной
    """
    if category.is_default:
        raise ValidationError(_('Нельзя изменять системные категории'))