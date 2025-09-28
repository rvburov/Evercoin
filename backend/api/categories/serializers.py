# evercoin/backend/api/categories/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Category, CategoryMerge


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий с дополнительными вычисляемыми полями
    """
    operation_count = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'icon',
            'color',
            'category_type',
            'description',
            'is_default',
            'is_active',
            'operation_count',
            'total_amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'is_default', 'created_at', 'updated_at', 
            'operation_count', 'total_amount'
        ]
    
    def validate(self, data):
        """
        Валидация данных категории
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        # Проверка уникальности названия категории для пользователя
        name = data.get('name')
        if name and user:
            existing_category = Category.objects.filter(user=user, name=name)
            if self.instance:  # При обновлении исключаем текущую категорию
                existing_category = existing_category.exclude(pk=self.instance.pk)
            
            if existing_category.exists():
                raise serializers.ValidationError({
                    'name': 'У вас уже есть категория с таким названием'
                })
        
        # Проверка, что пользователь не меняет системные категории
        if self.instance and self.instance.is_default:
            if 'name' in data and data['name'] != self.instance.name:
                raise serializers.ValidationError({
                    'name': 'Нельзя изменять название системной категории'
                })
            if 'category_type' in data and data['category_type'] != self.instance.category_type:
                raise serializers.ValidationError({
                    'category_type': 'Нельзя изменять тип системной категории'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Создание категории с автоматическим назначением пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class CategoryCreateSerializer(CategorySerializer):
    """
    Сериализатор для создания категорий
    """
    pass


class CategoryUpdateSerializer(CategorySerializer):
    """
    Сериализатор для обновления категорий
    """
    pass


class CategoryListSerializer(CategorySerializer):
    """
    Упрощенный сериализатор для списка категорий
    """
    class Meta(CategorySerializer.Meta):
        fields = [
            'id',
            'name',
            'icon',
            'color',
            'category_type',
            'is_default',
            'is_active',
            'operation_count',
            'total_amount'
        ]


class CategoryMergeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для слияния категорий
    """
    from_category_data = serializers.SerializerMethodField()
    to_category_data = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoryMerge
        fields = [
            'id',
            'from_category',
            'from_category_data',
            'to_category',
            'to_category_data',
            'operation_count',
            'merged_at'
        ]
        read_only_fields = ['id', 'operation_count', 'merged_at', 'user']
    
    def get_from_category_data(self, obj):
        """
        Получение данных об исходной категории
        """
        return {
            'id': obj.from_category.id,
            'name': obj.from_category.name,
            'icon': obj.from_category.icon,
            'color': obj.from_category.color,
            'category_type': obj.from_category.category_type
        }
    
    def get_to_category_data(self, obj):
        """
        Получение данных о целевой категории
        """
        return {
            'id': obj.to_category.id,
            'name': obj.to_category.name,
            'icon': obj.to_category.icon,
            'color': obj.to_category.color,
            'category_type': obj.to_category.category_type
        }
    
    def validate(self, data):
        """
        Валидация данных слияния
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        from_category = data.get('from_category')
        to_category = data.get('to_category')
        
        # Проверка владения категориями
        if from_category and from_category.user != user:
            raise serializers.ValidationError({
                'from_category': 'Вы не являетесь владельцем исходной категории'
            })
        
        if to_category and to_category.user != user:
            raise serializers.ValidationError({
                'to_category': 'Вы не являетесь владельцем целевой категории'
            })
        
        # Проверка, что категории разные
        if from_category and to_category and from_category == to_category:
            raise serializers.ValidationError({
                'to_category': 'Нельзя объединить категорию саму с собой'
            })
        
        # Проверка типа категорий
        if from_category and to_category and from_category.category_type != to_category.category_type:
            raise serializers.ValidationError({
                'to_category': 'Можно объединять только категории одного типа'
            })
        
        # Проверка, что исходная категория не системная
        if from_category and from_category.is_default:
            raise serializers.ValidationError({
                'from_category': 'Нельзя объединять системные категории'
            })
        
        return data
    
    def create(self, validated_data):
        """
        Создание записи о слиянии категорий
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        with transaction.atomic():
            from_category = validated_data['from_category']
            to_category = validated_data['to_category']
            
            # Переносим операции
            operation_count = from_category.operations.count()
            from_category.operations.update(category=to_category)
            
            # Создаем запись о слиянии
            validated_data['operation_count'] = operation_count
            category_merge = super().create(validated_data)
            
            # Удаляем исходную категорию
            from_category.delete()
        
        return category_merge


class CategoryDeleteSerializer(serializers.Serializer):
    """
    Сериализатор для обработки удаления категории
    """
    merge_with = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="ID категории для переноса операций"
    )
    delete_operations = serializers.BooleanField(
        default=False,
        help_text="Удалить все операции категории"
    )
    
    def validate_merge_with(self, value):
        """
        Валидация категории для переноса операций
        """
        if value:
            try:
                category = Category.objects.get(pk=value)
                request = self.context.get('request')
                if category.user != request.user:
                    raise serializers.ValidationError("Вы не являетесь владельцем этой категории")
                if category.category_type != self.context.get('category_type'):
                    raise serializers.ValidationError("Тип категории должен совпадать")
            except Category.DoesNotExist:
                raise serializers.ValidationError("Категория не найдена")
        return value


class CategoryBulkCreateSerializer(serializers.Serializer):
    """
    Сериализатор для массового создания категорий
    """
    categories = serializers.ListField(
        child=serializers.DictField(),
        help_text="Список категорий для создания"
    )
    
    def validate_categories(self, value):
        """
        Валидация списка категорий
        """
        for category_data in value:
            if 'name' not in category_data:
                raise serializers.ValidationError("Каждая категория должна иметь название")
            if 'category_type' not in category_data:
                raise serializers.ValidationError("Каждая категория должна иметь тип")
            if category_data['category_type'] not in ['income', 'expense']:
                raise serializers.ValidationError("Тип категории должен быть 'income' или 'expense'")
        
        return value
    
    def create(self, validated_data):
        """
        Массовое создание категорий
        """
        request = self.context.get('request')
        user = request.user if request else None
        
        categories_data = validated_data['categories']
        categories = []
        
        for category_data in categories_data:
            category = Category(
                user=user,
                name=category_data['name'],
                icon=category_data.get('icon', 'shopping'),
                color=category_data.get('color', '#4ECDC4'),
                category_type=category_data['category_type'],
                description=category_data.get('description', ''),
                is_default=False,
                is_active=True
            )
            categories.append(category)
        
        Category.objects.bulk_create(categories)
        return {'created_count': len(categories)}