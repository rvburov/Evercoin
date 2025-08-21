# project/backend/api/categories/serializers.py
from rest_framework import serializers
from .models import Category
from core.constants.icons import CATEGORY_ICONS
from core.constants.colors import CATEGORY_COLORS

class CategorySerializer(serializers.ModelSerializer):
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'operation_type', 'operation_type_display',
            'icon', 'color', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Проверка уникальности названия категории для пользователя"""
        user = self.context['request'].user
        operation_type = self.initial_data.get('operation_type')
        
        if self.instance:
            # При обновлении проверяем, кроме текущей категории
            if Category.objects.filter(
                user=user, 
                name=value, 
                operation_type=operation_type
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    'Категория с таким названием и типом уже существует'
                )
        else:
            # При создании
            if Category.objects.filter(
                user=user, 
                name=value, 
                operation_type=operation_type
            ).exists():
                raise serializers.ValidationError(
                    'Категория с таким названием и типом уже существует'
                )
        
        return value
    
    def validate_color(self, value):
        """Проверка формата цвета"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError('Неверный формат цвета. Используйте HEX формат (#RRGGBB)')
        return value

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'operation_type', 'icon', 'color']
    
    def validate_icon(self, value):
        """Проверка доступности иконки"""
        available_icons = [icon[0] for icon in CATEGORY_ICONS]
        if value not in available_icons:
            raise serializers.ValidationError('Выбранная иконка недоступна')
        return value
    
    def validate_color(self, value):
        """Проверка доступности цвета"""
        available_colors = [color[0] for color in CATEGORY_COLORS]
        if value not in available_colors:
            raise serializers.ValidationError('Выбранный цвет недоступен')
        return value

class CategoryWithStatsSerializer(CategorySerializer):
    operation_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['operation_count', 'total_amount']
