# project/backend/api/categories/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Category
from .serializers import (
    CategorySerializer,
    SimpleCategorySerializer,
    CategoryTreeSerializer
)

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    Представление для получения списка категорий и создания новой категории.
    Поддерживает фильтрацию по типу категории.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только категории текущего пользователя с возможностью фильтрации"""
        queryset = Category.objects.filter(user=self.request.user)
        
        # Фильтрация по типу категории
        category_type = self.request.query_params.get('type')
        if category_type in dict(Category.TYPE_CHOICES).keys():
            queryset = queryset.filter(type=category_type)
            
        return queryset.prefetch_related('children')

    def perform_create(self, serializer):
        """При создании автоматически привязываем категорию к пользователю"""
        serializer.save(user=self.request.user)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра, обновления и удаления категории.
    Запрещает удаление системных категорий.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ограничиваем доступ только к категориям текущего пользователя"""
        return Category.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Перед удалением проверяем, что категория не является системной"""
        if instance.is_system:
            raise permissions.PermissionDenied(
                "Нельзя удалить системную категорию"
            )
        
        # Переносим операции в категорию по умолчанию
        default_category = Category.objects.filter(
            user=self.request.user,
            is_system=True,
            type=instance.type
        ).first()
        
        if default_category:
            for operation in instance.operations.all():
                operation.category = default_category
                operation.save()
        
        instance.delete()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def category_tree(request):
    """
    Эндпоинт для получения древовидной структуры категорий.
    Возвращает только родительские категории с вложенными дочерними.
    """
    category_type = request.query_params.get('type')
    
    queryset = Category.objects.filter(
        user=request.user,
        parent__isnull=True  # Только родительские категории
    )
    
    if category_type in dict(Category.TYPE_CHOICES).keys():
        queryset = queryset.filter(type=category_type)
    
    serializer = CategoryTreeSerializer(queryset, many=True)
    return Response(serializer.data)
