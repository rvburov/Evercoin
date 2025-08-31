# evercoin/backend/api/categories/validators.py
from rest_framework import serializers


def validate_category_name_uniqueness(user, name, category_type, exclude_pk=None):
    """Проверка уникальности названия категории для пользователя и типа."""
    queryset = user.categories.filter(type=category_type)
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    
    if queryset.filter(name=name).exists():
        raise serializers.ValidationError(
            "Категория с таким названием и типом уже существует"
        )
    return name


def validate_category_name_length(value):
    """Проверка длины названия категории."""
    if len(value) > 255:
        raise serializers.ValidationError(
            "Название категории не может превышать 255 символов"
        )
    return value


def validate_icon(value):
    """Проверка допустимости иконки."""
    from api.core.constants.icons import CATEGORY_ICONS
    valid_icons = [icon[0] for icon in CATEGORY_ICONS]
    
    if value not in valid_icons:
        raise serializers.ValidationError("Недопустимая иконка")
    return value


def validate_color(value):
    """Проверка допустимости цвета."""
    from api.core.constants.colors import COLORS
    valid_colors = [color[0] for color in COLORS]
    
    if value not in valid_colors:
        raise serializers.ValidationError("Недопустимый цвет")
    return value
