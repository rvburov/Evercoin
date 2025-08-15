# project/backend/api/categories/serializers.py
from rest_framework import serializers
from .models import Category
from api.core.constants import icons, colors

class CategorySerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для категорий.
    Включает все поля и вложенные дочерние категории.
    """
    available_icons = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'type', 'icon', 'color',
            'parent', 'is_system', 'created_at',
            'available_icons', 'available_colors', 'children'
        ]
        read_only_fields = ['is_system', 'created_at']

    def get_available_icons(self, obj):
        """Возвращает список доступных иконок для фронтенда"""
        return icons.CATEGORY_ICONS

    def get_available_colors(self, obj):
        """Возвращает список доступных цветов для фронтенда"""
        return colors.CATEGORY_COLORS

    def get_children(self, obj):
        """Рекурсивно возвращает дочерние категории"""
        children = obj.children.all()
        serializer = self.__class__(children, many=True)
        return serializer.data

    def validate(self, data):
        """Дополнительная валидация данных категории"""
        if 'parent' in data and data.get('parent'):
            if data['parent'].type != data.get('type', self.instance.type if self.instance else None):
                raise serializers.ValidationError(
                    {'parent': 'Родительская категория должна быть того же типа'}
                )
        return data

class SimpleCategorySerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для использования в других моделях.
    Содержит только основные поля.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color']
        read_only_fields = fields

class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для древовидного представления категорий.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color', 'children']

    def get_children(self, obj):
        """Рекурсивно возвращает дочерние категории"""
        children = obj.children.all()
        serializer = self.__class__(children, many=True)
        return serializer.data
