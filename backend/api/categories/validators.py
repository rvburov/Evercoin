# project/backend/api/categories/filters.py
from rest_framework import serializers
from django.core.validators import validate_slug
import re

def validate_category_name(value):
    """
    Валидация названия категории
    - Минимум 2 символа
    - Максимум 100 символов
    - Разрешены буквы, цифры, пробелы и некоторые спецсимволы
    """
    if len(value) < 2:
        raise serializers.ValidationError('Название категории должно содержать минимум 2 символа')
    
    if len(value) > 100:
        raise serializers.ValidationError('Название категории не должно превышать 100 символов')
    
    # Проверка на допустимые символы
    if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-_\.\(\)]+$', value):
        raise serializers.ValidationError(
            'Название категории может содержать только буквы, цифры, пробелы и символы -_.()'
        )
    
    return value

def validate_hex_color(value):
    """Валидация HEX цвета"""
    if not value.startswith('#') or len(value) != 7:
        raise serializers.ValidationError('Неверный формат цвета. Используйте HEX формат (#RRGGBB)')
    
    # Проверка что все символы после # являются hex символами
    hex_part = value[1:]
    if not all(c in '0123456789ABCDEFabcdef' for c in hex_part):
        raise serializers.ValidationError('Неверный HEX код цвета')
    
    return value
