# evercoin/backend/api/categories/serializers.py
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import serializers

from api.operations.models import Operation

from .models import Category, CategoryBudget


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий с дополнительной статистикой."""
    
    operation_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    has_children = serializers.BooleanField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'type',
            'icon',
            'color',
            'parent',
            'parent_name',
            'is_default',
            'budget_limit',
            'description',
            'created_at',
            'updated_at',
            'operation_count',
            'total_amount',
            'has_children',
            'full_name'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Валидация уникальности названия категории для пользователя и типа."""
        user = self.context['request'].user
        category_type = self.initial_data.get('type')
        
        if not category_type:
            raise serializers.ValidationError("Тип категории обязателен")
        
        if self.instance:  # Редактирование существующей категории
            if Category.objects.filter(
                user=user,
                name=value,
                type=category_type
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Категория с таким названием и типом уже существует"
                )
        else:  # Создание новой категории
            if Category.objects.filter(
                user=user,
                name=value,
                type=category_type
            ).exists():
                raise serializers.ValidationError(
                    "Категория с таким названием и типом уже существует"
                )
        
        # Ограничение длины названия
        if len(value) > 255:
            raise serializers.ValidationError(
                "Название категории не может превышать 255 символов"
            )
        
        return value
    
    def validate_parent(self, value):
        """Валидация родительской категории."""
        if value:
            user = self.context['request'].user
            if value.user != user:
                raise serializers.ValidationError(
                    "Родительская категория должна принадлежать текущему пользователю"
                )
            
            # Проверка что родительская категория не является самой собой
            if self.instance and value.pk == self.instance.pk:
                raise serializers.ValidationError(
                    "Категория не может быть родителем самой себя"
                )
            
            # Проверка что родительская категория того же типа
            category_type = self.initial_data.get('type')
            if category_type and value.type != category_type:
                raise serializers.ValidationError(
                    "Родительская категория должна быть того же типа"
                )
        
        return value


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания категорий."""
    
    class Meta:
        model = Category
        fields = [
            'name',
            'type',
            'icon',
            'color',
            'parent',
            'budget_limit',
            'description'
        ]
    
    def create(self, validated_data):
        """Создание категории с привязкой к пользователю."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Сериализатор для древовидного представления категорий."""
    
    subcategories = serializers.SerializerMethodField()
    operation_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'type',
            'icon',
            'color',
            'parent',
            'operation_count',
            'total_amount',
            'subcategories'
        ]
    
    def get_subcategories(self, obj):
        """Рекурсивное получение подкатегорий."""
        subcategories = obj.subcategories.all()
        serializer = CategoryTreeSerializer(subcategories, many=True)
        return serializer.data


class CategoryWithStatsSerializer(serializers.ModelSerializer):
    """Сериализатор категорий со статистикой."""
    
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    operation_count = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'type',
            'icon',
            'color',
            'total_amount',
            'operation_count',
            'percentage'
        ]


class CategoryBudgetSerializer(serializers.ModelSerializer):
    """Сериализатор бюджетов категорий."""
    
    spent_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    remaining_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    progress_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    
    class Meta:
        model = CategoryBudget
        fields = [
            'id',
            'category',
            'category_name',
            'amount',
            'period',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at',
            'spent_amount',
            'remaining_amount',
            'progress_percentage'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Валидация данных бюджета."""
        category = data.get('category')
        period = data.get('period')
        end_date = data.get('end_date')
        
        if category and self.context['request'].user != category.user:
            raise serializers.ValidationError({
                "category": "Категория должна принадлежать текущему пользователю"
            })
        
        if period == 'custom' and not end_date:
            raise serializers.ValidationError({
                "end_date": "Для произвольного периода необходимо указать конечную дату"
            })
        
        if end_date and data.get('start_date') and end_date <= data['start_date']:
            raise serializers.ValidationError({
                "end_date": "Конечная дата должна быть позже начальной"
            })
        
        return data


class CategoryAnalyticsSerializer(serializers.Serializer):
    """Сериализатор для параметров аналитики категорий."""
    
    period = serializers.ChoiceField(
        choices=[
            ('all', 'Все'),
            ('year', 'Год'),
            ('month', 'Месяц'),
            ('week', 'Неделя'),
            ('day', 'День')
        ],
        default='all',
        required=False
    )
    wallet_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    category_type = serializers.ChoiceField(
        choices=[
            ('all', 'Все'),
            ('income', 'Доход'),
            ('expense', 'Расход')
        ],
        default='all',
        required=False
    )