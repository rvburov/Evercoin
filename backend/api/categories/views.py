# evercoin/backend/api/categories/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Category, CategoryMerge
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
    CategoryListSerializer,
    CategoryMergeSerializer,
    CategoryDeleteSerializer,
    CategoryBulkCreateSerializer
)
from .filters import CategoryFilter


class CategoryListView(generics.ListAPIView):
    """
    API endpoint для получения списка категорий пользователя
    """
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CategoryFilter
    ordering_fields = ['name', 'operation_count', 'created_at']
    ordering = ['category_type', 'name']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """
        Возвращает категории только текущего пользователя
        """
        return Category.objects.filter(user=self.request.user, is_active=True)


class CategoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей конкретной категории
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает категории только текущего пользователя
        """
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(generics.CreateAPIView):
    """
    API endpoint для создания новой категории
    """
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAuthenticated]


class CategoryUpdateView(generics.UpdateAPIView):
    """
    API endpoint для обновления существующей категории
    """
    serializer_class = CategoryUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает категории только текущего пользователя
        """
        return Category.objects.filter(user=self.request.user)


class CategoryDeleteView(generics.DestroyAPIView):
    """
    API endpoint для удаления категории с обработкой связанных операций
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает категории только текущего пользователя
        """
        return Category.objects.filter(user=self.request.user, is_default=False)
    
    def delete(self, request, *args, **kwargs):
        """
        Обработка удаления категории с опциями переноса операций
        """
        category = self.get_object()
        serializer = CategoryDeleteSerializer(
            data=request.data, 
            context={
                'request': request,
                'category_type': category.category_type
            }
        )
        
        if serializer.is_valid():
            return self._delete_category_with_options(category, serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _delete_category_with_options(self, category, options):
        """
        Удаление категории с выбранными опциями
        """
        from api.operations.models import Operation
        
        merge_with_id = options.get('merge_with')
        delete_operations = options.get('delete_operations', False)
        
        try:
            with transaction.atomic():
                # Проверяем наличие операций
                operation_count = category.operations.count()
                
                if operation_count == 0:
                    # Если операций нет, просто удаляем категорию
                    category.delete()
                    return Response(
                        {'message': 'Категория успешно удалена'}, 
                        status=status.HTTP_200_OK
                    )
                
                if delete_operations:
                    # Удаляем все операции категории
                    category.operations.all().delete()
                    category.delete()
                    return Response(
                        {'message': f'Категория и {operation_count} операций успешно удалены'}, 
                        status=status.HTTP_200_OK
                    )
                
                if merge_with_id:
                    # Переносим операции на другую категорию
                    merge_with_category = Category.objects.get(
                        pk=merge_with_id, 
                        user=self.request.user
                    )
                    
                    # Обновляем операции
                    Operation.objects.filter(category=category).update(category=merge_with_category)
                    
                    # Создаем запись о слиянии
                    CategoryMerge.objects.create(
                        user=self.request.user,
                        from_category=category,
                        to_category=merge_with_category,
                        operation_count=operation_count
                    )
                    
                    category.delete()
                    return Response(
                        {'message': f'Категория удалена, операции перенесены на {merge_with_category.name}'}, 
                        status=status.HTTP_200_OK
                    )
                
                # Если не выбрана опция, возвращаем ошибку
                return Response(
                    {
                        'error': 'Нельзя удалить категорию с привязанными операциями',
                        'operation_count': operation_count,
                        'options': {
                            'merge_with': 'ID категории для переноса операций',
                            'delete_operations': 'Удалить все операции категории'
                        }
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Ошибка при удалении категории: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryMergeView(generics.CreateAPIView):
    """
    API endpoint для слияния двух категорий
    """
    serializer_class = CategoryMergeSerializer
    permission_classes = [IsAuthenticated]


class CategoryBulkCreateView(generics.CreateAPIView):
    """
    API endpoint для массового создания категорий
    """
    serializer_class = CategoryBulkCreateSerializer
    permission_classes = [IsAuthenticated]


class CategoryByTypeView(generics.ListAPIView):
    """
    API endpoint для получения категорий по типу
    """
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает категории определенного типа для текущего пользователя
        """
        category_type = self.kwargs.get('type')
        if category_type not in ['income', 'expense']:
            return Category.objects.none()
        
        return Category.objects.filter(
            user=self.request.user, 
            category_type=category_type,
            is_active=True
        )


class CategoryToggleActiveView(generics.GenericAPIView):
    """
    API endpoint для активации/деактивации категории
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        """
        Переключение активности категории
        """
        category = get_object_or_404(Category, pk=pk, user=request.user)
        
        # Системные категории нельзя деактивировать
        if category.is_default:
            return Response(
                {'error': 'Нельзя деактивировать системную категорию'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category.is_active = not category.is_active
        category.save()
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)


class CategoryDefaultListView(generics.ListAPIView):
    """
    API endpoint для получения системных категорий
    """
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает системные категории для текущего пользователя
        """
        return Category.objects.filter(user=self.request.user, is_default=True, is_active=True)


@api_view(['POST'])
@transaction.atomic
def create_default_categories(request):
    """
    API endpoint для создания стандартных категорий для пользователя
    """
    # Проверяем, есть ли уже категории у пользователя
    if Category.objects.filter(user=request.user).exists():
        return Response(
            {'error': 'У вас уже есть категории'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        categories = Category.create_default_categories(request.user)
        serializer = CategoryListSerializer(categories, many=True)
        
        return Response({
            'message': f'Создано {len(categories)} стандартных категорий',
            'categories': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Ошибка при создании категорий: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def category_statistics(request):
    """
    API endpoint для получения статистики по категориям
    """
    from django.db.models import Count, Sum
    
    categories = Category.objects.filter(user=request.user, is_active=True)
    
    # Статистика по типам категорий
    type_stats = (
        categories.values('category_type')
        .annotate(
            category_count=Count('id'),
            total_operations=Sum('operations__amount'),
            operation_count=Count('operations')
        )
        .order_by('category_type')
    )
    
    # Самые используемые категории
    most_used_categories = (
        categories.annotate(
            operation_count=Count('operations'),
            total_amount=Sum('operations__amount')
        )
        .filter(operation_count__gt=0)
        .order_by('-operation_count')[:10]
    )
    
    most_used_data = [
        {
            'id': category.id,
            'name': category.name,
            'operation_count': category.operation_count,
            'total_amount': category.total_amount or 0,
            'category_type': category.category_type
        }
        for category in most_used_categories
    ]
    
    # Категории без операций
    unused_categories = categories.filter(operations__isnull=True).count()
    
    return Response({
        'type_statistics': list(type_stats),
        'most_used_categories': most_used_data,
        'unused_categories_count': unused_categories,
        'total_categories': categories.count()
    })